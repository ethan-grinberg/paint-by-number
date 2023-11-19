import { useState, useEffect } from 'react'
import "./Canvas.css"
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";
import { getFunctions, httpsCallable } from "firebase/functions";
import { ref, getDownloadURL } from "firebase/storage";
import storage from '../../firebaseConfig';
import { LoadingOverlay } from './Loading';

const minLoadingTime = 800

export function Canvas({fName}) {
    const [SvgComponent, setSvgComponent] = useState(null);
    const [idList, setIdList] = useState([]);
    const [loading, setLoading] = useState(false);

    const handleItemClick = (id, color) => {
        const element = document.getElementById(id);
        if (element) {
          element.setAttribute('fill', color);
        }
    };

    const fillColors = () => {
        for (const {color, shapes} of idList) {
            for (const id of shapes) {
                const element = document.getElementById(id);
                if (element) {
                    element.setAttribute('fill', `rgb${color}`)
                }
            }
        }
    }

    const clearColors = () => {
        for (const item of idList) {
            for (const id of item.shapes) {
                const element = document.getElementById(id);
                if (element) {
                    element.setAttribute('fill', "white")
                }
            }
        }
    }
    
    useEffect(() => {
        const importSvg = async () => {
            setLoading(true);
            try {
                if (fName.includes("src/assets/")) {
                    const [baseFile] = fName.split(".");
                    // eslint-disable-next-line no-unused-vars
                    const [component, jsonFile, _] =  await Promise.all(
                        [
                            import(`/${baseFile}.svg?react`), 
                            import(`/${baseFile}.json`), 
                            new Promise((resolve) => setTimeout(resolve, minLoadingTime))
                        ])
                    setLoading(false);
                    setIdList(jsonFile.default);
                    setSvgComponent(() => component.default);
                } else {
                    // load from bucket
                    const id = fName.substring(fName.indexOf("o/")+2, fName.lastIndexOf(".jpg"));

                    const functions = getFunctions();
                    const callableReturnMessage = httpsCallable(functions, 'generate_pbn');
                    const funcRes = await callableReturnMessage({"id": id});

                    // console.log(baseFile)
                    // const svgRef = ref(storage, `${id}.svg`);
                    // const jsonRef = ref(storage, `${id}.json`)
                    // const svgUrl = await getDownloadURL(svgRef);
                    // const jsonUrl = await getDownloadURL(jsonRef);
                    // console.log(svgRef);
                    // const [component, jsonFile, _] =  await Promise.all(
                    //     [
                    //         fetch(svgRef), 
                    //         fetch(jsonRef)
                    //     ])
                    // console.log(component);
                    // console.log(jsonFile)
                    // setLoading(false);
                    // setIdList(jsonFile.default);
                    // setSvgComponent(() => component.default);
                }
            } catch (error) {
              console.error('Error importing SVG/JSON:', error);
            }
          };
        
        importSvg();

    }, [fName])
    
      useEffect(() => {
        // Loop through the list of IDs and add event listeners
        for (const {color, shapes} of idList) {
            for (const id of shapes) {
                const element = document.getElementById(id);
                if (element) {
                    element.addEventListener('click', () => handleItemClick(id, `rgb${color}`))
                }
            }
        }
    
        // Cleanup: Remove event listeners when the component unmounts
        return () => {
            for (const {color, shapes} of idList) {
                for (const id of shapes) {
                    const element = document.getElementById(id);
                    if (element) {
                        element.removeEventListener('click', () => handleItemClick(id, `rgb${color}`))
                    }
                }
            }
        };
      }, [idList]);
      
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
                    <img src="src/assets/escape.png" width={15}/>
                </button>             
            </div>
            {loading && <LoadingOverlay></LoadingOverlay>}
            {!loading && <div className='svg-container'>
                <TransformComponent>
                    {SvgComponent && (<SvgComponent className='svg-element'/>)}
                </TransformComponent>
            </div>}
        </div>
        )}
        </TransformWrapper>
    )
}