import { Canvas } from './components/Canvas'
import { useState } from 'react'
import './App.css'

const dir = "src/assets"
let imageFiles = ["panda", "landscape", "flower", "portrait"];
imageFiles = imageFiles.map(item => `${dir}/${item}.jpg`);

function App() {
  const [currImage, setCurrImage] = useState(imageFiles[0]);
  const [images, setImages] = useState(imageFiles);
  
  function selectImage(image) {
    setCurrImage(image);
  }

  return (
    <div className='app-container'>
      <div className='image-carousel'>
          {images.map((item, index) => (
            <div key={index} className='carousel-item'>
              <img src={item} onClick={() => selectImage(item)} className={`carousel-img ${currImage === item ? 'selected' : ''}`}/>
            </div>
          ))}
      </div>
      <div className='canvas'>
        <Canvas fName={currImage}></Canvas>
      </div>
    </div>
  )
}

export default App
