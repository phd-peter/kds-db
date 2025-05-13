'use client';

import LaTeXRenderer from './LaTeXRenderer';

interface SearchResult {
  id: string;
  text: string;
  distance: number;
  metadata: {
    type?: string;
    level?: number;
    doc_id?: string;
    [key: string]: any;
  };
  source?: string;
  match_count?: number;
}

interface SearchResultsProps {
  results: SearchResult[];
  isLoading: boolean;
}

export default function SearchResults({ results, isLoading }: SearchResultsProps) {
  if (isLoading) {
    return (
      <div className="w-full max-w-3xl mt-8 p-6 rounded-lg border border-gray-200 shadow-sm">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-500"></div>
          <span className="ml-3">검색 중...</span>
        </div>
      </div>
    );
  }

  if (results.length === 0) {
    return (
      <div className="w-full max-w-3xl mt-8 p-6 rounded-lg border border-gray-200 shadow-sm">
        <p className="text-center text-gray-500">검색 결과가 없습니다.</p>
      </div>
    );
  }

  return (
    <div className="w-full max-w-3xl mt-8">
      <p className="mb-4 text-gray-600">{results.length}개의 결과를 찾았습니다.</p>
      <div className="space-y-4">
        {results.map((result) => (
          <div key={result.id} className="p-6 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-lg font-medium mb-2">문서 ID: {result.id}</h3>
                <div className="flex flex-wrap gap-2 mb-2">
                  {result.source && (
                    <span className={`inline-block px-2 py-1 text-xs rounded-full ${
                      result.source === 'vector' 
                        ? 'bg-blue-100 text-blue-800'
                        : result.source === 'keyword'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-purple-100 text-purple-800'
                    }`}>
                      {result.source === 'vector' 
                        ? '벡터 검색' 
                        : result.source === 'keyword' 
                        ? '키워드 검색' 
                        : '하이브리드'}
                    </span>
                  )}
                  {result.metadata.type && (
                    <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded-full">
                      {result.metadata.type}
                    </span>
                  )}
                  {result.metadata.level && (
                    <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded-full">
                      Level: {result.metadata.level}
                    </span>
                  )}
                  {result.metadata.doc_id && (
                    <span className="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-800 rounded-full">
                      문서: {result.metadata.doc_id}
                    </span>
                  )}
                </div>
              </div>
              <div className="text-right">
                <span className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                  유사도: {(1 - result.distance).toFixed(4)}
                </span>
                {result.match_count !== undefined && (
                  <span className="inline-block ml-2 px-2 py-1 text-xs bg-green-100 text-green-800 rounded-full">
                    키워드 매치: {result.match_count}
                  </span>
                )}
              </div>
            </div>
            <div className="mt-3 text-gray-700">
              <LaTeXRenderer content={result.text} className="whitespace-pre-wrap" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
