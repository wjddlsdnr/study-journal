// src/api.ts
const API_BASE = import.meta.env.VITE_API_BASE;

export const uploadImage = async (file: File) => {
  const formData = new FormData();
  formData.append("file", file);
  const token = localStorage.getItem("access_token");
  return fetch(`${API_BASE}/upload/`, {
    method: "POST",
    headers: { "token": token || "" },
    body: formData,
  });
};


export const searchSentences = async (query: string) => {
  const token = localStorage.getItem("access_token");
  const res = await fetch(`${API_BASE}/semantic_search/?query=` + encodeURIComponent(query), {
    headers: { "token": token || "" },
  });
  if (!res.ok) throw new Error("검색 실패");
  const data = await res.json();
  if (!Array.isArray(data)) throw new Error("검색 결과 형식 오류");
  return data;
};


export const deleteImage = (filename: string, token?: string) =>
  fetch(`${API_BASE}/delete_image/${filename}`, {
    method: "DELETE",
    headers: { token: token || "" },
  });


export const fetchHighlightedImage = async (image_path: string, query: string) => {
  const token = localStorage.getItem("access_token");
  const res = await fetch(`${API_BASE}/highlighted_image/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "token": token || "",
    },
    body: JSON.stringify({ image_path, query }),
  });
  return res.blob();
};



export const fetchMyImages = (token?: string) =>
  fetch(`${API_BASE}/my_images/`, {
    headers: { token: token || "" },
  }).then(res => res.json());
