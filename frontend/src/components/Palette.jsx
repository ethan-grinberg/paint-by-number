import React from "react";
import "./Palette.css";

const paletteItemStyles = (currentColor, color) => {
  return {
    backgroundColor: `rgb${color}`,
    border: `${currentColor === color ? "2px" : "0"} solid #646cff`,
  };
};

const overlayStyles = (percentage) => ({
  position: 'absolute',
  top: 0,
  left: 0,
  height: '100%',
  width: '100%',
  background: `conic-gradient(white ${percentage}%, transparent ${percentage}%)`,
  clipPath: 'circle(50% at center)',
  zIndex: 2,
  opacity: '30%'
})


const Palette = ({ idList, currentColor, setCurrentColor, colorCount }) => {
  return (
    <div className="palette-container">
      {idList.map((value, idx) => {
        if (idx === 0) return null;
          {
            return (colorCount[value.color] / value.shapes.length === 0) ? 
            <img src="/check.png" className="completed-item"/>
            :
            <div
              key={idx}
              className="palette-item"
              style={paletteItemStyles(currentColor, value.color)}
              onClick={() => setCurrentColor(value.color)}
            >
              <div style={overlayStyles((colorCount[value.color] / value.shapes.length) * 100)} />
              {idx}
            </div>
          }
      })}
    </div>
  );
};

export default Palette;
