import React, { useState, useRef, useCallback } from 'react';
import { Upload, Search, Image as ImageIcon, Type, X, Download, Info } from 'lucide-react';
import axios from 'axios';

interface SearchResult {
  id: string;
  url: string;
  similarity: number;
  title?: string;
  description?: string;
  category?: string;
  source?: string;
}

function App() {
  const [searchMode, setSearchMode] = useState<'text' | 'image'>('text');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setSelectedImage(reader.result as string);
        setError(null);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSearch = useCallback(async () => {
    if (searchMode === 'text' && !searchQuery.trim()) {
      setError('Please enter a search query');
      return;
    }
    
    if (searchMode === 'image' && !selectedImage) {
      setError('Please select an image');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    try {
      const payload = {
        query: searchMode === 'text' ? searchQuery : selectedImage,
        type: searchMode
      };

      const response = await axios.post('http://localhost:5000/api/search', payload, {
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.data.results && response.data.results.length > 0) {
        setResults(response.data.results);
      } else {
        setError('No results found');
        setResults([]);
      }
    } catch (error) {
      console.error('Error searching:', error);
      setError('Error searching. Please try again.');
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  }, [searchMode, searchQuery, selectedImage]);

  const handleDownload = async (url: string, title: string) => {
    try {
      const response = await fetch(url);
      const blob = await response.blob();
      const blobUrl = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = blobUrl;
      link.download = `${title.replace(/\s+/g, '-').toLowerCase()}.jpg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(blobUrl);
    } catch (error) {
      console.error('Error downloading image:', error);
    }
  };

  return (
    // <div className="min-h-screen bg-gradient-to-br from-[#0f2027] via-[#203a43] to-[#2c5364]">
    <div className="min-h-screen bg-gradient-to-br from-[#000428] via-[#004e92] to-[#000428]">
 
 <nav className="bg-white/5 backdrop-blur-md border-b border-white/10 shadow-md">
  <div className="container mx-auto px-2 py-2 flex justify-between items-center">
  <div className="flex items-center space-x-3">
  <img 
    src="/logo.png" 
    alt="MediVerse Logo" 
    className="w-16 h-16 object-cover rounded-full border-2 border-white/20 shadow-sm"
  />
  <span className="text-3xl font-bold bg-gradient-to-r from-[#7CB342] to-[#00FFAA] bg-clip-text text-transparent tracking-tight">
    MediVerse
  </span>
</div>

    
  </div>
</nav>


      <div className="container mx-auto px-4 py-12">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h1 className="text-5xl md:text-6xl font-bold text-white mb-4">
              Visual Learning&nbsp;              
              <span className="text-[#7CB342] bg-gradient-to-r from-[#7CB342] to-[#00FFAA] bg-clip-text text-transparent">Search Engine</span>
            </h1>
            <p className="text-3xl text-white/80 max-w-2xl mx-auto">
            <b>Navigating the Medical Multiverse</b>
            </p> 
          </div>

          <div className="bg-[#c5e3f6] rounded-2xl p-8 mb-12 border border-[#5ebef7] shadow-[0_4px_14px_rgba(94,190,247,0.4)]">


            <div className="flex gap-4 mb-8">
              <button
                onClick={() => {  
                  setSearchMode('text');
                  setError(null);
                }}
                className={`flex-1 py-4 px-6 rounded-xl flex items-center justify-center gap-3 transition-all duration-300 ${
                  searchMode === 'text'
                    ? 'bg-[#005B96] text-white shadow-lg transform hover:scale-105'
                    : 'bg-[#E6F2F8] text-[#005B96] hover:bg-[#00A3AD] hover:text-white'
                }`}
              >
                <Type size={24} />
                <span className="text-lg font-medium">Text Search</span>
              </button>
              <button
                onClick={() => {
                  setSearchMode('image');
                  setError(null);
                }}
                className={`flex-1 py-4 px-6 rounded-xl flex items-center justify-center gap-3 transition-all duration-300 ${
                  searchMode === 'image'
                    ? 'bg-[#005B96] text-white shadow-lg transform hover:scale-105'
                    : 'bg-[#E6F2F8] text-[#005B96] hover:bg-[#00A3AD] hover:text-white'
                }`}
              >
                <ImageIcon size={24} />
                <span className="text-lg font-medium">Image Search</span>
              </button>
            </div>

            {error && (
              <div className="mb-4 p-4 bg-red-50 text-red-600 rounded-lg">
                {error}
              </div>
            )}

            {searchMode === 'text' ? (
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search images..."
                  className="w-full px-6 py-4 text-lg rounded-xl border-2 border-[#E6F2F8] focus:border-[#00A3AD] transition-all duration-300 outline-none"
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
                <button
                  onClick={handleSearch}
                  disabled={isLoading}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-[#00A3AD] text-white p-3 rounded-lg hover:bg-[#005B96] transition-all duration-300 disabled:opacity-50"
                >
                  {isLoading ? (
                    <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  ) : (
                    <Search size={24} />
                  )}
                </button>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-4">
                <div 
                  className={`image-upload-area flex flex-col items-center justify-center rounded-xl p-12 transition-all duration-300 w-full ${
                    selectedImage 
                      ? 'bg-transparent' 
                      : 'bg-[#E6F2F8] hover:bg-[#E6F2F8]/80 border-2 border-dashed border-[#00A3AD] cursor-pointer'
                  }`}
                  onClick={() => !selectedImage && fileInputRef.current?.click()}
                >
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleImageUpload}
                    accept="image/*"
                    className="hidden"
                  />
                  {selectedImage ? (
                    <div className="relative group">
                      <img
                        src={selectedImage}
                        alt="Selected"
                        className="max-h-80 rounded-lg shadow-xl"
                      />
                      <div className="absolute top-2 right-2 flex gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setSelectedImage(null);
                          }}
                          className="bg-red-500/90 text-white p-2 rounded-full shadow-lg hover:bg-red-600 transition-all transform hover:scale-110"
                        >
                          <X size={20} />
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center">
                      <Upload size={48} className="text-[#00A3AD] mx-auto mb-4" />
                      <p className="text-xl font-medium text-[#005B96] mb-2">Upload an image to search</p>
                      <p className="text-gray-500">Drag & drop or click to browse</p>
                    </div>
                  )}
                </div>
                {selectedImage && (
                  <button
                    onClick={handleSearch}
                    disabled={isLoading}
                    className="bg-[#00A3AD] text-white px-8 py-4 rounded-xl hover:bg-[#005B96] transition-all duration-300 disabled:opacity-50 flex items-center gap-2"
                  >
                    {isLoading ? (
                      <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <>
                        <Search size={24} />
                        <span>Search Similar Images</span>
                      </>
                    )}
                  </button>
                )}
              </div>
            )}
          </div>

          {results.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {results.map((result) => (
                <div
                  key={result.id}
                  className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all duration-300"
                >
                  <div className="relative">
                    <img
                      src={result.url}
                      alt={result.title}
                      className="w-full h-48 object-cover"
                    />
                    <div className="absolute bottom-2 left-2 bg-[#00A3AD] text-white text-xs px-2 py-1 rounded-full">
                      {Math.round(result.similarity * 100)}% Match
                    </div>
                    {result.source && (
                      <div className="absolute top-2 right-2 bg-black/50 text-white text-xs px-2 py-1 rounded-full">
                        {result.source}
                      </div>
                    )}
                  </div>
                  <div className="p-4">
                    <h3 className="text-[#005B96] font-semibold mb-2">{result.title || 'Untitled'}</h3>
                    {result.description && (
                      <p className="text-sm text-gray-600 mb-3">{result.description}</p>
                    )}
                    <div className="flex justify-between items-center">
                      <button
                        onClick={() => handleDownload(result.url, result.title || 'image')}
                        className="text-[#00A3AD] hover:text-[#005B96] transition-colors"
                      >
                        <Download size={20} />
                      </button>
                      {result.category && (
                        <span className="text-sm text-gray-500">{result.category}</span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;