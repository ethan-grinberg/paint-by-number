import { Grid } from  'react-loader-spinner'

export function LoadingOverlay({loadingStr}) {
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
            {loadingStr}
        </div>
      </div>
    );
}