import type { Prediction } from "../../services/inferenceApi";
import '../shared/PanelStyles.css'
import './RecognitionPanel.css'

type Props = {
  cameraReady: boolean;
  isRecognizing: boolean;
  isConfirming: boolean;
  prediction: Prediction | null;
};

export function RecognitionPanel({
  cameraReady,
  isRecognizing,
  isConfirming,
  prediction,
}: Props) {
  const title = prediction
    ? "Recognized sign"
    : cameraReady
      ? isConfirming
        ? "Confirming sign…"
        : isRecognizing
          ? "Recognizing sign…"
          : "Waiting for a camera frame"
      : "Waiting for your camera";
  const copy = prediction
    ? `${Math.round(prediction.confidence * 100)}% confidence · ${prediction.model_version} · confirmed across recent frames`
    : cameraReady
      ? isConfirming
        ? "Hold the sign steady while recent confident frames are compared."
        : "The local API is analyzing sampled camera frames."
      : "Open your camera, then hold one supported sign in the frame.";

  return (
    <section
      className="recognition-panel"
      aria-labelledby="recognition-panel-title"
      aria-live="polite"
    >
      <div className="panel-heading">
        <div className="panel-title">
          <span className="step-badge muted">02</span>
          <h3 id="recognition-panel-title">Recognized sign</h3>
        </div>
        <span className="panel-hint">MODEL OUTPUT</span>
      </div>
      <div className="recognition-result">
        <span className="result-icon" aria-hidden="true">
          ⌁
        </span>
        <div>
          <p className="result-title">{title}</p>
          <p className="result-copy">{copy}</p>
        </div>
        <div className="predicted-word" aria-label="Predicted sign">
          {prediction?.label ?? "—"}
        </div>
      </div>
      <p className="scope-note">
        <i className="scope-dot" />
        Confirms stable isolated signs across frames. It does not interpret sign
        motion or translate sentences.
      </p>
    </section>
  );
}
