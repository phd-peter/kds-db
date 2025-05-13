'use client';

import { useState } from 'react';
import SearchForm from './components/SearchForm';
import SearchResults from './components/SearchResults';

interface SearchResult {
  id: string;
  text: string;
  distance: number;
  metadata: Record<string, any>;
  source?: string;
  match_count?: number;
}

export default function Home() {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchPerformed, setSearchPerformed] = useState(false);

  const handleSearch = async (query: string, searchType: string) => {
    setIsLoading(true);
    setSearchPerformed(true);
    
    try {
      // 백엔드 API URL
      // 실제 배포 시에는 /api/search로 설정하여 Next.js에서 Python 백엔드로 프록시
      const apiUrl = `/api/search?query=${encodeURIComponent(query)}&search_type=${searchType}&limit=10`;
      
      // 개발 중에는 직접 Python 서버에 요청할 수도 있음
      // const apiUrl = `http://localhost:5000/search?query=${encodeURIComponent(query)}&search_type=${searchType}&limit=10`;
      
      const response = await fetch(apiUrl);
      
      if (!response.ok) {
        throw new Error('검색 중 오류가 발생했습니다.');
      }
      
      const data = await response.json();
      setResults(data.results || []);
    } catch (error) {
      console.error('검색 오류:', error);
      // 실제 환경에서는 사용자에게 오류 메시지를 보여줘야 함
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen py-8 px-4 flex flex-col items-center">
      <header className="mb-12 text-center">
        <h1 className="text-3xl font-bold mb-2">KDS 문서 검색</h1>
        <p className="text-gray-600">벡터 검색, 키워드 검색, 하이브리드 검색을 지원합니다.</p>
      </header>
      
      <main className="flex flex-col items-center w-full max-w-4xl mx-auto">
        <SearchForm onSearch={handleSearch} isLoading={isLoading} />
        
        {searchPerformed && (
          <SearchResults results={results} isLoading={isLoading} />
        )}
        
        {!searchPerformed && (
          <div className="mt-16 text-center text-gray-500">
            <p className="mb-4">검색어를 입력하여 KDS 문서를 검색해보세요.</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 max-w-2xl mx-auto mt-8">
              <div className="p-4 border border-gray-200 rounded-lg shadow-sm">
                <h3 className="font-medium mb-2">벡터 검색</h3>
                <p className="text-sm text-gray-600">의미 기반 검색으로 유사한 내용을 찾습니다.</p>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg shadow-sm">
                <h3 className="font-medium mb-2">키워드 검색</h3>
                <p className="text-sm text-gray-600">문자열 매칭으로 정확한 단어를 포함한 결과를 찾습니다.</p>
              </div>
              <div className="p-4 border border-gray-200 rounded-lg shadow-sm">
                <h3 className="font-medium mb-2">하이브리드 검색</h3>
                <p className="text-sm text-gray-600">벡터와 키워드 검색을 결합하여 최적의 결과를 제공합니다.</p>
              </div>
            </div>
          </div>
        )}
      </main>
      
      <footer className="mt-16 text-center text-gray-500 text-sm">
        <p>© 2025 KDS 문서 검색 시스템</p>
      </footer>
    </div>
  );
}
