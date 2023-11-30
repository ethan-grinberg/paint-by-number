import { Canvas } from "./components/Canvas";
import { useEffect, useState } from "react";
import uuid from 'react-uuid';
import storage from "../firebaseConfig"
import { ref, uploadBytes, getDownloadURL } from "firebase/storage";
import { LoadingOverlay } from './components/Loading';
import "./App.css";
import Palette from "./components/Palette";

const dir = ".";
let imageFiles = ["panda", "landscape", "flower", "portrait"];
const images = imageFiles.map(item => `${dir}/${item}.jpg`);

function App() {
  const [currImage, setCurrImage] = useState(images[0]);
  const [idList, setIdList] = useState([]);
  const [currentColor, setCurrentColor] = useState();
  const [colorCount, setColorCount] = useState({});
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [userImages, setUserImages] = useState([]);


  useEffect(() => {
    const counts = idList.reduce((acc, value) => {
      acc[value.color] = value.shapes.length;
      return acc;
    }, {});
    
    setColorCount(counts);
  }, [idList]);

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
      if (!(image.type === "image/jpeg" || image.type === "image/png")) {
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
        Try adding your own images! (must be in jpg or png format)
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
      <div className="canvas">
      {
        !loading && 
          <Palette
            idList={idList}
            currentColor={currentColor}
            setCurrentColor={setCurrentColor}
            colorCount={colorCount}
          />
      }
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
    </div>
  );
}

export default App;
