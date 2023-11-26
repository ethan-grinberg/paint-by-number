import { Canvas } from "./components/Canvas";
import { useEffect, useState } from "react";
import "./App.css";
import Palette from "./components/Palette";

const images = ["panda", "landscape", "flower", "portrait"];
const dir = "src/assets";

function App() {
  const [currImage, setCurrImage] = useState("panda");
  const [idList, setIdList] = useState([]);
  const [currentColor, setCurrentColor] = useState();
  const [colorCount, setColorCount] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const counts = idList.reduce((acc, value) => {
      acc[value.color] = value.shapes.length;
      return acc;
    }, {});
    
    setColorCount(counts);
  }, [idList]);

  function selectImage(image) {
    setCurrImage(image);
  }

  return (
    <div className="app-container">
      <div className="image-carousel">
        {images.map((item, index) => (
          <div key={index} className="carousel-item">
            <img
              src={`${dir}/${item}.jpg`}
              onClick={() => selectImage(item)}
              className={`carousel-img ${currImage === item ? "selected" : ""}`}
            />
          </div>
        ))}
      </div>
      <div className="canvas">
        <Canvas
          fName={currImage}
          currentColor={currentColor}
          setIdList={setIdList}
          idList={idList}
          setColorCount={setColorCount}
          loading={loading}
          setLoading={setLoading}
        />
      </div>
      {
        !loading && 
          <Palette
            idList={idList}
            currentColor={currentColor}
            setCurrentColor={setCurrentColor}
            colorCount={colorCount}
          />
      }
    </div>
  );
}

export default App;
