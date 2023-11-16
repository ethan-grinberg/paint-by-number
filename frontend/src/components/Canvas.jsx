import { useState, useEffect } from 'react'
import "./Canvas.css"
import idList from "../assets/panda.json"
import PandaSVG from '../assets/panda.svg?react'

export function Canvas() {
    // const [SvgComponent, setSvg] = useState(null);
    // const [idList, setIdList] = useState([]);

    const handleItemClick = (id, color) => {
        const element = document.getElementById(id);
        if (element) {
          // Change the color or any other attribute based on the provided color
          element.setAttribute('fill', color);
        }
    };
    
    // useEffect(() => {
    //     const importSvg = async () => {
    //         try {
    //           // Dynamically import the SVG file as a React component
    //           const svg = await import(`../assets/${fName}.svg`);
    //           const json = await import(`../assets/${fName}.json`)

    //           setIdList(json.default);
    //           setSvg(svg.default);
    //         } catch (error) {
    //           console.error('Error importing SVG/JSON:', error);
    //         }
    //       };
        
    //     importSvg();

    // }, [fName])
    
      useEffect(() => {
        // Loop through the list of IDs and add event listeners
        for (const {color, shapes} of idList) {
            console.log(color)
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
      }, []);
      
    return (
        <div className='canvas-container'>
            <PandaSVG className="canvas"></PandaSVG>
        </div>
    )
}