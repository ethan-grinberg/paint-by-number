import { useState, useEffect, useRef } from "react";
import "./Canvas.css";
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";
import { getFunctions, httpsCallable } from "firebase/functions";
import { ref, getDownloadURL } from "firebase/storage";
import storage from '../../firebaseConfig';
import { LoadingOverlay } from './Loading';
import axios from 'axios';

const minLoadingTime = 800


export const Canvas = ({
  fName,
  setIdList,
  idList,
  currentColor,
  setColorCount,
  loading,
  setLoading,
}) => {
  const [svgString, setSvgString] = useState(null);
  const currentColorRef = useRef(currentColor);
  const [errorMsg, setErrorMsg] = useState(null);

  const handleItemClick = (id, color) => {
    const element = document.getElementById(id);
    if (element && element.getAttribute('fill') === 'lightpink') {
      element.setAttribute("fill", color);
      setColorCount((prevCount) => ({
        ...prevCount,
        [currentColorRef.current]: prevCount[currentColorRef.current] - 1,
      }));
    }
  };

  const fillColors = () => {
    for (const { color, shapes } of idList) {
      for (const id of shapes) {
        const element = document.getElementById(id);
        if (element) {
          element.setAttribute("fill", `rgb${color}`);
          setColorCount(prevCount => {
            const filledCount = {}
            Object.keys(prevCount).forEach(color => filledCount[color] = 0)
            return filledCount
          })
        }
      }
    }
  };

  const clearColors = () => {
    for (const item of idList) {
      for (const id of item.shapes) {
        const element = document.getElementById(id);
        if (element) {
          element.setAttribute("fill", "white");
          const counts = idList.reduce((acc, value) => {
            acc[value.color] = value.shapes.length;
            return acc;
          }, {});
          setColorCount(counts)
        }
      }
    }
  };

  const updatePathStrokes = (currentColor) => {
    idList.forEach(({ color, shapes }) => {
      shapes.forEach((id) => {
        const element = document.getElementById(id);
        const elementFill = element.getAttribute('fill')
        const isElementFilled = elementFill !== 'white' && elementFill !== 'lightpink'
        if (element && !isElementFilled) {  
          element.setAttribute('fill', color === currentColor ? 'lightpink' : 'white');          
        }
      });
    });
  };
  

  useEffect(() => {
    currentColorRef.current = currentColor;
    updatePathStrokes(currentColor)
  }, [currentColor]);


  useEffect(() => {
    // Loop through the list of IDs and add event listeners
    for (const { color, shapes } of idList) {
      for (const id of shapes) {
        const element = document.getElementById(id);
        if (element) {
          element.addEventListener("click", () =>
            handleItemClick(id, `rgb${color}`)
          );
        }
      }
    }

     // Cleanup: Remove event listeners when the component unmounts
     return () => {
      for (const { color, shapes } of idList) {
        for (const id of shapes) {
          const element = document.getElementById(id);
          if (element) {
            element.removeEventListener("click", () =>
              handleItemClick(id, `rgb${color}`)
            );
          }
        }
      }
    };
  }, [idList])
    
    useEffect(() => {
        const importSvg = async () => {
            setLoading(true);
            setErrorMsg(null);
            try {
                if (!fName.includes("http")) {
                    const baseFile = fName.split("./")[1].split(".jpg")[0]
                    // eslint-disable-next-line no-unused-vars
                    const [component, jsonFile, _] =  await Promise.all(
                        [
                            import(`../assets/${baseFile}.svg?raw`), 
                            import(`../assets/${baseFile}.json`), 
                            new Promise((resolve) => setTimeout(resolve, minLoadingTime))
                        ])
                    setIdList(jsonFile.default);
                    setSvgString(component.default)
                } else {
                    // load from bucket
                    const imageFile = fName.substring(fName.indexOf("o/")+2, fName.lastIndexOf("?"))
                    const id = imageFile.split(".")[0]
                    const svgRef = ref(storage, `${id}.svg`);
                    const jsonRef = ref(storage, `${id}.json`);
                    
                    // call cloud function to convert image to pbn if not already computed
                    let svgUrl;
                    let jsonUrl;
                    try {
                        // retrieve results from bucket if already computed
                        const results = await Promise.all([getDownloadURL(svgRef), getDownloadURL(jsonRef)]);
                        svgUrl = results[0]
                        jsonUrl = results[1];
                    } catch (err) {
                        const functions = getFunctions();
                        const callableReturnMessage = httpsCallable(functions, 'make_pbn');
                        // eslint-disable-next-line no-unused-vars
                        const funcRes = await callableReturnMessage({"id": imageFile});

                        const results = await Promise.all([getDownloadURL(svgRef), getDownloadURL(jsonRef)]);
                        svgUrl = results[0]
                        jsonUrl = results[1];
                    }
                    // retrieve results from bucket
                    const [svgRes, jsonRes] = await Promise.all([axios.get(svgUrl), axios.get(jsonUrl)])

                    // update component data
                    setIdList(jsonRes.data);
                    setSvgString(svgRes.data);
                }
            } catch (error) {
                setErrorMsg("Error generating paint by number, try again later or try a smaller image size");
                console.error('Error importing SVG/JSON:', error);
            } finally{
                setLoading(false);
            }
          };
        
        importSvg();
  }, [fName]);

  return (
    <TransformWrapper
      initialScale={1}
      initialPositionX={0}
      initialPositionY={0}
    >
      {
        // eslint-disable-next-line no-unused-vars
        ({ zoomIn, zoomOut, resetTransform, ...rest }) => (
        <div className='canvas-container'>
            <div className='controls'>
                <button onClick={() => clearColors()}> 
                    Clear
                </button>  
                <button onClick={() => fillColors()}>
                    Fill
                </button>
                <button onClick={() => resetTransform()}>
                    <img src="./escape.png" width={15}/>
                </button>             
            </div>
            {loading && <LoadingOverlay loadingStr={"Generating Paint By Number..."}></LoadingOverlay>}
            {!loading && <div className='svg-container'>
                <TransformComponent>
                    {errorMsg ? (<div> {errorMsg} </div>) 
                    : (<div dangerouslySetInnerHTML={{ __html: svgString }} className='svg-element'></div>)}
                </TransformComponent>
              </div>
            }
          </div>
        )
      }
    </TransformWrapper>
  );
};
