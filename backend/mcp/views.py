from rest_framework import generics, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse
import csv
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import Transaction
from ai.sql_agent import run_query_nl


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'


class TransactionView(generics.ListAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer


class QueryTransactionsView(APIView):
    
    @extend_schema(
        summary="Выполнить естественно-языковой SQL запрос",
        description="Преобразует текстовый запрос на естественном языке в SQL и возвращает результаты",
        parameters=[
            OpenApiParameter(
                name='q',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=True,
                description='Текстовый запрос на естественном языке (например: "дай транзакции за последний месяц My Favorite Bank")',
            ),
            OpenApiParameter(
                name='format',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                required=False,
                description='Формат ответа: json или csv (по умолчанию json)',
                enum=['json', 'csv'],
            ),
        ],
        responses={
            200: {
                'description': 'Успешный ответ',
                'content': {
                    'application/json': {
                        'example': {
                            'data': [
                                {
                                    'transaction_id': '123e4567-e89b-12d3-a456-426614174000',
                                    'transaction_timestamp': '2023-12-01T10:00:00Z',
                                    'issuer_bank_name': 'My Favorite Bank',
                                    'transaction_amount_kzt': '1500.00',
                                }
                            ],
                            'sql': 'SELECT * FROM mcp_transactions WHERE issuer_bank_name = \'My Favorite Bank\' LIMIT 1000;',
                            'error': None
                        }
                    }
                }
            },
            400: {
                'description': 'Ошибка запроса',
                'content': {
                    'application/json': {
                        'example': {
                            'data': [],
                            'sql': '',
                            'error': 'Параметр \'q\' обязателен'
                        }
                    }
                }
            }
        }
    )
    def get(self, request):
        query = request.GET.get("q")
        format_ = request.GET.get("format", "json")
        
        print(f"🔍 QueryTransactionsView GET request:")
        print(f"   query: {query}")
        print(f"   format: {format_}")
        print(f"   request.GET: {dict(request.GET)}")
        
        if not query:
            return JsonResponse({
                "error": "Параметр 'q' обязателен",
                "data": [],
                "sql": ""
            }, status=400)
        
        # Выполняем запрос через SQL агента
        result = run_query_nl(query)
        print(f"🔍 SQL Agent result: data count = {len(result.get('data', []))}, error = {result.get('error')}")
        
        # Если есть ошибка
        if result.get("error"):
            return JsonResponse(result, status=400)
        
        data = result.get("data", [])
        
        # Если формат CSV
        if format_ == "csv":
            if not data:
                return HttpResponse("Нет данных для экспорта", status=404)
            
            response = HttpResponse(content_type="text/csv; charset=utf-8")
            response["Content-Disposition"] = 'attachment; filename="transactions.csv"'
            
            # Записываем CSV
            writer = csv.DictWriter(response, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
            
            return response
        
        # Возвращаем JSON
        return JsonResponse(result, safe=False)