import { Canvas } from './components/Canvas'
import { useState, useEffect } from 'react'
import uuid from 'react-uuid';
import storage from "../firebaseConfig"
import { ref, uploadBytes, getDownloadURL } from "firebase/storage";
import { LoadingOverlay } from './components/Loading';
import './App.css'

const dir = "."
let imageFiles = ["panda", "landscape", "flower", "portrait"];
const images = imageFiles.map(item => `${dir}/${item}.jpg`);

function App() {
  const [currImage, setCurrImage] = useState(images[0]);
  const [userImages, setUserImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    // Retrieve array from local storage on component mount
    let localImages = localStorage.getItem('userImages');
    if (localImages) {
      localImages = JSON.parse(localImages)
      setUserImages(localImages);
    }
  }, []);

  function selectImage(image) {
    setCurrImage(image);
  }

  async function handleImageFile(e) {
    setLoading(true);
    setErrorMsg(null);
    try {
      const image = e.target.files[0];
      if (!image.type.includes("image")) {
        throw new Error("not an image");
      }
      // eslint-disable-next-line no-unused-vars
      const [_, extension] = image.name.split(".")
      const fileName = `${uuid()}.${extension}`;
      const imageRef = ref(storage, fileName);

      const res = await uploadBytes(imageRef, image);
      const url = await getDownloadURL(res.ref);

      const updatedUserImages = [url, ...userImages]
      setUserImages(updatedUserImages);
      localStorage.setItem('userImages', JSON.stringify(updatedUserImages));
    } catch (err) {
      setErrorMsg("Error importing image, make sure it is in JPG format")
      console.log(err)
    } finally{
      setLoading(false)
    }
  }

  return (
    <div className='app-container'>
      {loading && <LoadingOverlay loadingStr={"Uploading Image..."}></LoadingOverlay>}
      <p>
        Try adding your own images!
      </p>
      {errorMsg && <p> {errorMsg} </p>}
      <form>
        <input 
          type="file"
          onChange={handleImageFile}
        />
      </form>
      <div className='image-carousel'>
          {[...userImages, ...images].map((item, index) => (
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
