import { Canvas } from './components/Canvas'
import { useState } from 'react'
import './App.css'

const images = ["panda", "landscape", "flower", "portrait"]
const dir = "src/assets"

function App() {
  const [currImage, setCurrImage] = useState("panda");
  function selectImage(image) {
    setCurrImage(image);
  }

  return (
    <div className='app-container'>
      <div className='image-carousel'>
          {images.map((item, index) => (
            <div key={index} className='carousel-item'>
              <img src={`${dir}/${item}.jpg`} className='select-image' onClick={() => selectImage(item)}/>
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
