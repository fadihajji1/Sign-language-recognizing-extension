import '../shared/PanelStyles.css'
import './GeneratedOutput.css'

type Props = { signHistory: string[]; onClear: () => void }

export function GeneratedOutput({ signHistory, onClear }: Props) {
  return (
    <section className="generated-output" aria-labelledby="generated-output-title" aria-live="polite">
      <div className="panel-heading">
        <div className="panel-title"><span className="step-badge muted">03</span><h3 id="generated-output-title">Recent confirmed signs</h3></div>
        {signHistory.length > 0 && <button className="clear-signs" onClick={onClear}>Clear</button>}
      </div>
      <div className="output-surface" aria-live="polite">
        {signHistory.length ? (
          <ol className="sign-history">
            {signHistory.map((label, index) => <li key={`${label}-${index}`}>{label}</li>)}
          </ol>
        ) : <p>Confirmed signs will appear here as you sign.</p>}
      </div>
      <p className="output-note">Shows changes between stable labels. It does not detect sign boundaries, preserve repeated signs, or translate a sentence.</p>
    </section>
  )
}
