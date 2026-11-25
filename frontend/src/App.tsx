import { AboutNote } from './components/AboutNote/AboutNote'
import { BrandHeader } from './components/BrandHeader/BrandHeader'
import { CameraRecognition } from './components/CameraRecognition/CameraRecognition'
import './App.css'

function App() {
  return (
    <div className="site-shell" id="top">
      <BrandHeader />
      <main>
        <section className="hero-section">
          <p className="eyebrow"><span /> TUNISIAN SIGN LANGUAGE <b>·</b> CAMERA RECOGNITION</p>
          <h1>Every gesture<br />has <em>something to say.</em></h1>
          <p className="hero-copy">Sign in front of your camera. The system checks recent frames and shows a supported sign when the predictions agree.</p>
          <div className="hero-facts"><span>✳ &nbsp;57 supported signs</span><i />Stable sign recognition</div>
        </section>

        <section className="workspace" aria-labelledby="workspace-title">
          <div className="workspace-heading">
            <div><p className="section-label">WORKSPACE <span>01</span></p><h2 id="workspace-title">Live recognition</h2></div>
            <p className="privacy-label"><span aria-hidden="true">◈</span> Camera frames are not saved</p>
          </div>
          <CameraRecognition />
          <div className="workspace-caption"><span>✳ &nbsp;Built for research, with care.</span><span>W7CH dataset &nbsp;·&nbsp; 57 classes</span></div>
        </section>
        <AboutNote />
      </main>
      <footer className="site-footer"><span>TSL RECOGNITION <b>/</b> ACADEMIC PROJECT</span><span>Made to learn. Built to keep improving.</span></footer>
    </div>
  )
}

export default App
