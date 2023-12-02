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
      <div className="title-container">
        <h1>
          PBNgen
        </h1>
        <a href="https://github.com/ethan-grinberg/paint-by-number" style={{marginLeft: 10}}>
          <img src={"/github-logo.png"} width={50}/>
        </a>
      </div>
      <h2 style={{fontWeight:250}}>
        Automatically generate paint by numbers from your images and color them in
      </h2>
      <ul className="instructions-container">
        <li className="instructions-item">
          Upload your image in jpg or png format
        </li>
        <li className="instructions-item">
          In this version high resolution images might time out or take a while
        </li>
        <li className="instructions-item">
          The application might say you are not finished with a certain color even when you cannot see anymore shapes to fill in.
          <br/>
          This is because automatically generating paint by numbers can create very small shapes.
        </li>
      </ul>
      {loading && <LoadingOverlay loadingStr={"Uploading Image..."}></LoadingOverlay>}
      {/* <h3>
        Try adding your own images
      </h3> */}
      {errorMsg && <p> {errorMsg} </p>}
      <form>
        <input 
          type="file"
          onChange={handleImageFile}
        />
      </form>
      {/* <p>
        Note: Your images must be in jpg or png format 
        <br></br>
        and very high resolution images might take a while or time out
      </p> */}
      <div className='image-carousel'>
          {[...userImages, ...images].map((item, index) => (
            <div key={index} className='carousel-item'>
              <img src={item} onClick={() => selectImage(item)} className={`carousel-img ${currImage === item ? 'selected' : ''}`}/>
            </div>
          ))}
      </div>
      <div className="palette-container">
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
    </div>
  );
}

export default App;
