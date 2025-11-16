import { useState } from 'react';
import { aiChatbotApi, type DeepQueryResponse } from '@/api/ai-chatbot';
import { Layers, CheckCircle2, XCircle, AlertCircle, Loader2, Download, Copy, BookOpen } from 'lucide-react';

interface DeepQueryProps {
  databaseId: number;
}

// Pre-built templates for common use cases
const QUERY_TEMPLATES = {
  etl_validation: {
    name: 'ETL Schema Validation',
    description: 'Verify source schema before ETL pipeline',
    includeListTables: true,
    includeTableInfo: true,
    tableNames: '',
    sql: 'SELECT COUNT(*) as total_rows FROM your_table;',
  },
  migration_check: {
    name: 'Migration Validation',
    description: 'Compare database schemas across environments',
    includeListTables: true,
    includeTableInfo: true,
    tableNames: '',
    sql: 'SELECT table_name, column_name, data_type FROM information_schema.columns ORDER BY table_name;',
  },
  data_quality: {
    name: 'Data Quality Audit',
    description: 'Check for NULLs, duplicates, and orphaned records',
    includeListTables: false,
    includeTableInfo: true,
    tableNames: '',
    sql: `SELECT 'NULL check' as check_type, COUNT(*) as issues
FROM your_table WHERE critical_column IS NULL
UNION ALL
SELECT 'Duplicates', COUNT(*) - COUNT(DISTINCT id) FROM your_table;`,
  },
  onboarding: {
    name: 'Developer Onboarding',
    description: 'Explore database for new team members',
    includeListTables: true,
    includeTableInfo: true,
    tableNames: '',
    sql: 'SELECT * FROM your_main_table LIMIT 10;',
  },
};

export function DeepQuery({ databaseId }: DeepQueryProps) {
  const [sqlQuery, setSqlQuery] = useState('');
  const [tableNames, setTableNames] = useState('');
  const [includeListTables, setIncludeListTables] = useState(true);
  const [includeTableInfo, setIncludeTableInfo] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<DeepQueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showTemplates, setShowTemplates] = useState(false);

  const loadTemplate = (templateKey: keyof typeof QUERY_TEMPLATES) => {
    const template = QUERY_TEMPLATES[templateKey];
    setIncludeListTables(template.includeListTables);
    setIncludeTableInfo(template.includeTableInfo);
    setTableNames(template.tableNames);
    setSqlQuery(template.sql);
    setShowTemplates(false);
  };

  const exportSchema = () => {
    if (!result) return;

    const schemaData = result.results
      .filter(r => r.operation === 'table_info')
      .map(r => ({
        operation: r.operation,
        result: r.result,
        tables: r.tables_queried,
      }));

    const blob = new Blob([JSON.stringify(schemaData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `schema_export_${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const copyResults = async () => {
    if (!result) return;

    const text = JSON.stringify(result, null, 2);
    await navigator.clipboard.writeText(text);
    alert('Results copied to clipboard!');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!sqlQuery.trim()) {
      setError('Please enter a SQL query');
      return;
    }

    const operations = [];

    // Add list_tables operation
    if (includeListTables) {
      operations.push({ type: 'list_tables' as const });
    }

    // Add table_info operation
    if (includeTableInfo) {
      const tables = tableNames
        .split(',')
        .map(t => t.trim())
        .filter(Boolean);

      if (tables.length === 0) {
        setError('Please specify at least one table name for Table Info operation');
        return;
      }

      operations.push({
        type: 'table_info' as const,
        tables,
      });
    }

    // Add query operation
    operations.push({
      type: 'query' as const,
      sql: sqlQuery.trim(),
    });

    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await aiChatbotApi.runDeepQuery({
        database_id: databaseId,
        operations,
      });

      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Failed to execute deep query');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="h-full flex flex-col bg-black text-white">
      {/* Header */}
      <div className="border-b border-gray-800 bg-gray-900/50 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 p-2">
              <Layers className="h-5 w-5 text-white" />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Deep Query</h2>
              <p className="text-sm text-gray-400">
                ETL validation, migrations, data quality audits, and more
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowTemplates(!showTemplates)}
              className="flex items-center gap-2 rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-300 transition-colors hover:bg-gray-700"
            >
              <BookOpen className="h-4 w-4" />
              Templates
            </button>
            {result && (
              <>
                <button
                  onClick={exportSchema}
                  className="flex items-center gap-2 rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-300 transition-colors hover:bg-gray-700"
                >
                  <Download className="h-4 w-4" />
                  Export
                </button>
                <button
                  onClick={copyResults}
                  className="flex items-center gap-2 rounded-lg border border-gray-700 bg-gray-800 px-3 py-2 text-sm text-gray-300 transition-colors hover:bg-gray-700"
                >
                  <Copy className="h-4 w-4" />
                  Copy
                </button>
              </>
            )}
          </div>
        </div>

        {/* Template Dropdown */}
        {showTemplates && (
          <div className="mt-4 rounded-lg border border-gray-700 bg-gray-800 p-4">
            <h3 className="text-sm font-medium text-white mb-3">Use Case Templates</h3>
            <div className="grid gap-2">
              {Object.entries(QUERY_TEMPLATES).map(([key, template]) => (
                <button
                  key={key}
                  onClick={() => loadTemplate(key as keyof typeof QUERY_TEMPLATES)}
                  className="text-left rounded-lg border border-gray-700 bg-gray-900/50 p-3 transition-colors hover:bg-gray-700"
                >
                  <div className="font-medium text-white text-sm">{template.name}</div>
                  <div className="text-xs text-gray-400 mt-1">{template.description}</div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="mx-auto max-w-4xl space-y-6">
          {/* Configuration Form */}
          <div className="rounded-lg border border-gray-800 bg-gray-900/50 p-6">
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Operation Checkboxes */}
              <div className="space-y-3">
                <h3 className="text-sm font-medium text-gray-300">Operations</h3>

                <label className="flex items-center gap-3 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={includeListTables}
                    onChange={(e) => setIncludeListTables(e.target.checked)}
                    className="h-4 w-4 rounded border-gray-700 bg-gray-800 text-purple-500 focus:ring-2 focus:ring-purple-500 focus:ring-offset-0 focus:ring-offset-gray-900"
                  />
                  <span className="text-sm text-gray-300 group-hover:text-white transition-colors">
                    List all tables
                  </span>
                </label>

                <label className="flex items-center gap-3 cursor-pointer group">
                  <input
                    type="checkbox"
                    checked={includeTableInfo}
                    onChange={(e) => setIncludeTableInfo(e.target.checked)}
                    className="h-4 w-4 rounded border-gray-700 bg-gray-800 text-purple-500 focus:ring-2 focus:ring-purple-500 focus:ring-offset-0 focus:ring-offset-gray-900"
                  />
                  <span className="text-sm text-gray-300 group-hover:text-white transition-colors">
                    Get table info (schema)
                  </span>
                </label>
              </div>

              {/* Table Names Input */}
              {includeTableInfo && (
                <div className="space-y-2">
                  <label htmlFor="table-names" className="block text-sm font-medium text-gray-300">
                    Table Names (comma-separated)
                  </label>
                  <input
                    id="table-names"
                    type="text"
                    value={tableNames}
                    onChange={(e) => setTableNames(e.target.value)}
                    placeholder="e.g., users, transactions, products"
                    className="w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                  />
                </div>
              )}

              {/* SQL Query Input */}
              <div className="space-y-2">
                <label htmlFor="sql-query" className="block text-sm font-medium text-gray-300">
                  SQL Query <span className="text-red-500">*</span>
                </label>
                <textarea
                  id="sql-query"
                  value={sqlQuery}
                  onChange={(e) => setSqlQuery(e.target.value)}
                  placeholder="SELECT * FROM users WHERE city = 'Almaty' LIMIT 10;"
                  rows={6}
                  className="w-full rounded-lg border border-gray-700 bg-gray-800 px-4 py-2.5 text-sm text-white placeholder-gray-500 font-mono focus:border-purple-500 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                />
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full rounded-lg bg-gradient-to-r from-purple-500 to-pink-500 px-4 py-2.5 text-sm font-medium text-white transition-all hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Executing...
                  </>
                ) : (
                  'Run Deep Query'
                )}
              </button>
            </form>
          </div>

          {/* Error Message */}
          {error && (
            <div className="rounded-lg border border-red-900/50 bg-red-900/20 p-4 flex items-start gap-3">
              <XCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-medium text-red-400">Error</h4>
                <p className="text-sm text-red-300 mt-1">{error}</p>
              </div>
            </div>
          )}

          {/* Results */}
          {result && (
            <div className="space-y-4">
              {/* Summary Card */}
              <div className={`rounded-lg border p-4 ${
                result.all_successful
                  ? 'border-green-900/50 bg-green-900/20'
                  : 'border-yellow-900/50 bg-yellow-900/20'
              }`}>
                <div className="flex items-center gap-3">
                  {result.all_successful ? (
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-yellow-500" />
                  )}
                  <div className="flex-1">
                    <h4 className={`text-sm font-medium ${
                      result.all_successful ? 'text-green-400' : 'text-yellow-400'
                    }`}>
                      {result.all_successful ? 'All operations successful' : 'Some operations failed'}
                    </h4>
                    <div className="mt-1 flex items-center gap-4 text-xs text-gray-400">
                      <span>Total: {result.total_operations}</span>
                      <span>Executed: {result.executed_operations}</span>
                      <span>✓ {result.successful_operations}</span>
                      <span>✗ {result.failed_operations}</span>
                      <span>{result.total_execution_time_ms}ms</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Operation Results */}
              <div className="space-y-3">
                {result.results.map((opResult, idx) => (
                  <div
                    key={idx}
                    className={`rounded-lg border p-4 ${
                      opResult.success
                        ? 'border-gray-800 bg-gray-900/50'
                        : opResult.skipped
                        ? 'border-gray-700 bg-gray-800/30'
                        : 'border-red-900/50 bg-red-900/20'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div className="flex-shrink-0 mt-0.5">
                        {opResult.success ? (
                          <CheckCircle2 className="h-4 w-4 text-green-500" />
                        ) : opResult.skipped ? (
                          <AlertCircle className="h-4 w-4 text-gray-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <h5 className="text-sm font-medium text-white">
                            {idx + 1}. {opResult.operation.replace('_', ' ').toUpperCase()}
                          </h5>
                          {opResult.execution_time_ms && (
                            <span className="text-xs text-gray-500">
                              {opResult.execution_time_ms}ms
                            </span>
                          )}
                        </div>

                        {/* Operation-specific content */}
                        {opResult.success && opResult.operation === 'list_tables' && opResult.tables && (
                          <div className="mt-2">
                            <p className="text-xs text-gray-400 mb-1">
                              Found {opResult.count} tables:
                            </p>
                            <div className="flex flex-wrap gap-1.5">
                              {opResult.tables.map((table, i) => (
                                <span
                                  key={i}
                                  className="inline-flex items-center rounded-md bg-purple-500/10 px-2 py-1 text-xs font-mono text-purple-400 border border-purple-500/20"
                                >
                                  {table}
                                </span>
                              ))}
                            </div>
                          </div>
                        )}

                        {opResult.success && opResult.operation === 'table_info' && opResult.result && (
                          <div className="mt-2">
                            <pre className="text-xs text-gray-400 overflow-x-auto whitespace-pre-wrap bg-gray-800/50 rounded p-2 border border-gray-700">
                              {typeof opResult.result === 'string'
                                ? opResult.result
                                : JSON.stringify(opResult.result, null, 2)}
                            </pre>
                          </div>
                        )}

                        {opResult.success && opResult.operation === 'query' && (
                          <div className="mt-2 space-y-2">
                            {opResult.sql && (
                              <div>
                                <p className="text-xs text-gray-400 mb-1">SQL:</p>
                                <pre className="text-xs text-purple-400 font-mono bg-gray-800/50 rounded p-2 border border-gray-700 overflow-x-auto">
                                  {opResult.sql}
                                </pre>
                              </div>
                            )}
                            {opResult.result && (
                              <div>
                                <p className="text-xs text-gray-400 mb-1">Result:</p>
                                <pre className="text-xs text-gray-300 font-mono bg-gray-800/50 rounded p-2 border border-gray-700 overflow-x-auto max-h-60">
                                  {typeof opResult.result === 'string'
                                    ? opResult.result
                                    : JSON.stringify(opResult.result, null, 2)}
                                </pre>
                              </div>
                            )}
                          </div>
                        )}

                        {opResult.error && (
                          <p className="mt-2 text-xs text-red-400">{opResult.error}</p>
                        )}

                        {opResult.skipped && (
                          <p className="mt-2 text-xs text-gray-500">
                            Skipped due to previous failure
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
