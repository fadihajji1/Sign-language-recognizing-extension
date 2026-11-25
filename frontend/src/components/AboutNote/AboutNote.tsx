import './AboutNote.css'

export function AboutNote() {
  return (
    <section className="about-note" id="about">
      <span className="about-icon" aria-hidden="true">ⓘ</span>
      <div className="about-copy">
        <strong>A research prototype, not a translator.</strong>
        <p>The model predicts one isolated dataset sign at a time. It does not understand continuous signing or full sentences.</p>
      </div>
    </section>
  )
}
