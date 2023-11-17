import { useState, useEffect } from 'react'
import "./Canvas.css"
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";
import { Grid } from  'react-loader-spinner'

const LoadingOverlay = () => {
    return (
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          background: 'rgba(0,0,0,0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          flexDirection: 'column',
          zIndex: 9999,
        }}
      >
        <Grid
            height="100"
            width="100"
            color="#646cff"
            ariaLabel="grid-loading"
            radius="12.5"
            wrapperClass=""
            visible={true}
            wrapperStyle={{margin: 20}}
        />
        <div>
            Processing...
        </div>
      </div>
    );
  };

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
            setLoading(true)
            try {
                // eslint-disable-next-line no-unused-vars
                const [component, jsonFile, _] =  await Promise.all(
                    [
                        import(`/src/assets/${fName}.svg?react`), 
                        import(`/src/assets/${fName}.json`), 
                        new Promise((resolve) => setTimeout(resolve, 800))
                    ])
                setLoading(false);
                setIdList(jsonFile.default);
                setSvgComponent(() => component.default);
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