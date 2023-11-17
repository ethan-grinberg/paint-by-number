import { useState, useEffect } from 'react'
import "./Canvas.css"
import { TransformWrapper, TransformComponent } from "react-zoom-pan-pinch";

export function Canvas({fName}) {
    const [SvgComponent, setSvgComponent] = useState(null);
    const [idList, setIdList] = useState([]);

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
            try {
                const component = await import(`/src/assets/${fName}.svg?react`);
                const jsonFile = await import(`/src/assets/${fName}.json`)
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
        <div className='canvas-container'>
            <div className='controls'>
                <button onClick={() => clearColors()}> 
                    Clear
                </button>  
                <button onClick={() => fillColors()}>
                    Fill
                </button>               
            </div>
            <div className='svg-container'>
                <TransformWrapper >
                    <TransformComponent>
                        {SvgComponent && (<SvgComponent className='svg-element'/>)}
                    </TransformComponent>
                </TransformWrapper>

            </div>
        </div>

    )
}