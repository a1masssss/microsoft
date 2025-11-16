import { Layers, Download } from 'lucide-react';
import { useTelegram } from '../hooks/useTelegram';
import { AdvancedTools } from '../components/AdvancedTools';

export const DeepQueryPage = () => {
  const { hapticFeedback, showAlert } = useTelegram();
  const databaseId = 1;

  return (
    <div className="min-h-screen bg-gray-50">
      <section className="border-b border-gray-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-4 px-4 py-8">
          <div className="flex items-center gap-4">
            <div className="rounded-2xl bg-gradient-to-r from-[#ff9966] to-[#ff5e62] p-3 text-white">
              <Layers className="h-6 w-6" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-widest text-gray-500">SQL Toolkit</p>
              <h1 className="text-2xl font-semibold text-gray-900">Глубокий запрос</h1>
              <p className="text-sm text-gray-500">
                Выполняйте цепочки операций и экспортируйте результаты в один клик.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4 rounded-2xl border border-gray-100 bg-gray-50 px-4 py-3 text-sm text-gray-600">
            <Download className="h-4 w-4 text-gray-500" />
            Используйте глубокий запрос, чтобы сначала изучить схему, затем выполнить SQL и
            подготовить CSV/Excel отчёт.
          </div>
        </div>
      </section>

      <div className="mx-auto w-full max-w-5xl px-4 py-8">
        <AdvancedTools
          databaseId={databaseId}
          hapticFeedback={hapticFeedback}
          showAlert={showAlert}
        />
      </div>
    </div>
  );
};
