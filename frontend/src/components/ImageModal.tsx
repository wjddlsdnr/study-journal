import React from "react";

interface Props {
  imageUrl: string;
  onClose: () => void;
}
const ImageModal: React.FC<Props> = ({ imageUrl, onClose }) => {
  // 이미지가 없는 경우 안내 메시지 표시
  const [error, setError] = React.useState(false);

  React.useEffect(() => {
    setError(false); // 새 이미지 열 때 에러 초기화
  }, [imageUrl]);

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-70 z-50">
      <div className="relative">
        {!error ? (
          <img
            src={imageUrl}
            alt="확대 이미지"
            className="rounded-2xl shadow-2xl max-w-[90vw] max-h-[90vh] object-contain border-4 border-yellow-300"
            onError={() => setError(true)}
          />
        ) : (
          <div className="flex flex-col items-center justify-center w-[60vw] h-[60vh] bg-white bg-opacity-80 rounded-2xl shadow-2xl">
            <span className="text-red-500 text-xl font-bold mb-4">이미지를 불러올 수 없습니다.</span>
            <span className="text-gray-500 break-all">{imageUrl}</span>
          </div>
        )}
        <button
          className="absolute top-3 right-3 bg-white bg-opacity-80 rounded-full px-5 py-2 text-gray-800 font-bold text-lg shadow-lg hover:bg-yellow-400 hover:text-white"
          onClick={onClose}
        >
          닫기
        </button>
      </div>
    </div>
  );
};

export default ImageModal;
