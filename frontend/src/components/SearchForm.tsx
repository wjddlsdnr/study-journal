// SearchForm.tsx
import { useState } from "react";
import { searchSentences } from "../api"; // import


interface Props {
  onResults: (data: any[]) => void;
}
const SearchForm: React.FC<Props> = ({ onResults }) => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    try {
      const data = await searchSentences(query);
      onResults(data);
    } catch {
      onResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSearch} className="flex flex-col items-center gap-2">
      <label className="block w-full text-center font-semibold mb-2 text-lg text-blue-700">이미지 내 문장 검색</label>
      <input
        type="text"
        placeholder="예: 저항 공식, 인터럽트, NOR, 3.3kΩ, ..."
        value={query}
        onChange={e => setQuery(e.target.value)}
        className="w-full border-2 border-blue-200 rounded-lg p-2 bg-blue-50"
        disabled={loading}
      />
      <button
        type="submit"
        disabled={loading}
        className="mt-2 px-4 py-2 bg-blue-500 text-white rounded-full shadow hover:bg-blue-600 font-bold transition"
      >
        {loading ? "검색 중..." : "검색"}
      </button>
    </form>
  );
};

export default SearchForm;
