import { Canvas } from './components/Canvas'
import { useState } from 'react'
import uuid from 'react-uuid';
import storage from "../firebaseConfig"
import { ref, uploadBytes, getDownloadURL } from "firebase/storage";
import { LoadingOverlay } from './components/Loading';
import './App.css'

const dir = "src/assets"
let imageFiles = ["panda", "landscape", "flower", "portrait"];
imageFiles = imageFiles.map(item => `${dir}/${item}.jpg`);

function App() {
  const [currImage, setCurrImage] = useState(imageFiles[0]);
  const [images, setImages] = useState(imageFiles);
  const [loading, setLoading] = useState(false);

  function selectImage(image) {
    setCurrImage(image);
  }

  async function handleImageFile(e) {
    const image = e.target.files[0];

    if (!image.type.includes("image")) {
      console.log("not an image");
      return;
    }

    setLoading(true);
    try {
      // eslint-disable-next-line no-unused-vars
      const [_, extension] = image.name.split(".")
      const fileName = `${uuid()}.${extension}`;
      const imageRef = ref(storage, fileName);

      const res = await uploadBytes(imageRef, image);
      const url = await getDownloadURL(res.ref);

      // const functions = getFunctions();
      // const callableReturnMessage = httpsCallable(functions, 'generate_pbn');
      // const funcRes = await callableReturnMessage({"id": fileName});

      setImages([url, ...images]);
    } catch (err) {
      console.log(err)
    } finally{
      setLoading(false)
    }
  }

  return (
    <div className='app-container'>
      {loading && <LoadingOverlay></LoadingOverlay>}
      <p>
        Try adding your own image! (this functionality is currently not implemented)
      </p>
      <form>
        <input 
          type="file"
          onChange={handleImageFile}
        />
      </form>
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
