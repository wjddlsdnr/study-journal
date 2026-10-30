import { useRef, useState } from "react";
// import { uploadImage } from "../api";  // 불필요하므로 제거!
const API_BASE = import.meta.env.VITE_API_BASE;

const UploadForm = () => {
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fileInputRef.current?.files?.length) return;
    setUploading(true);

    const formData = new FormData();
    formData.append("file", fileInputRef.current.files[0]);

    const token = localStorage.getItem("access_token");

    try {
      const res = await fetch(API_BASE + "/upload/", {
        method: "POST",
        headers: {
          "token": token || "",
        },
        body: formData,
      });
      if (res.ok) {
        alert("✅ 업로드 성공! 검색에서 확인해보세요.");
        fileInputRef.current.value = "";
      } else {
        alert("❌ 업로드 실패: " + (await res.text()));
      }
    } catch (err) {
      alert("❌ 업로드 중 오류");
    } finally {
      setUploading(false);
    }
  };

  return (
    <form onSubmit={handleUpload} className="flex flex-col items-center gap-2">
      <label className="block w-full text-center font-semibold mb-2 text-lg text-blue-700">이미지 업로드</label>
      <input
        type="file"
        accept="image/*"
        ref={fileInputRef}
        className="w-full border-2 border-yellow-200 rounded-lg p-2 bg-yellow-50"
        disabled={uploading}
      />
      <button
        type="submit"
        disabled={uploading}
        className="mt-2 px-4 py-2 bg-yellow-400 text-white rounded-full shadow hover:bg-yellow-500 font-bold transition"
      >
        {uploading ? "업로드 중..." : "업로드"}
      </button>
    </form>
  );
};

export default UploadForm;
