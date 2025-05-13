'use client';

import { useState } from 'react';

interface SearchFormProps {
  onSearch: (query: string, searchType: string) => void;
  isLoading: boolean;
}

export default function SearchForm({ onSearch, isLoading }: SearchFormProps) {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('hybrid');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query, searchType);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-3xl">
      <div className="flex flex-col gap-4 w-full">
        <div className="flex flex-col md:flex-row gap-3">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="검색어를 입력하세요..."
            className="flex-1 px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 shadow-sm"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed shadow-sm transition-colors font-medium"
          >
            {isLoading ? '검색 중...' : '검색'}
          </button>
        </div>
        
        <div className="flex flex-wrap gap-3">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="searchType"
              value="vector"
              checked={searchType === 'vector'}
              onChange={() => setSearchType('vector')}
              className="h-4 w-4 text-blue-600"
            />
            <span>벡터 검색</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="searchType"
              value="keyword"
              checked={searchType === 'keyword'}
              onChange={() => setSearchType('keyword')}
              className="h-4 w-4 text-blue-600"
            />
            <span>키워드 검색</span>
          </label>
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="radio"
              name="searchType"
              value="hybrid"
              checked={searchType === 'hybrid'}
              onChange={() => setSearchType('hybrid')}
              className="h-4 w-4 text-blue-600"
            />
            <span>하이브리드 검색 (벡터 + 키워드)</span>
          </label>
        </div>
      </div>
    </form>
  );
}
