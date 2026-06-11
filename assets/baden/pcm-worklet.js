// PCM capture worklet for Baden-mode audio notes (next.html → bdStartRecording).
//
// Raw, untouched Float32 PCM straight off the input — no resampling, no gain,
// no compression. The main thread accumulates these frames and encodes an
// uncompressed PCM WAV at the AudioContext's native sample rate. We deliberately
// do NOT use MediaRecorder, whose Safari default is lossy AAC-in-MP4: this note
// is a preservation master, so the goal is to prevent any FURTHER loss past the
// iPad microphone (which is itself the fidelity ceiling — WAV adds no quality).
//
// Mono: we read channel 0 only. Frames arrive in 128-sample render quanta; each
// is copied and transferred (zero-copy) to the main thread to avoid GC churn.
//
// The node is given ONE output that we leave as silence and connect to the
// context destination. That connection is what guarantees the audio graph keeps
// pulling process() on a real-time context — a capture-only node with no output
// path can be dropped from rendering and then no frames ever arrive. We do NOT
// pass the input through to the output, so nothing is played back (no echo).
class PCMCapture extends AudioWorkletProcessor {
  process(inputs /*, outputs */) {
    const ch = inputs[0] && inputs[0][0];
    if (ch && ch.length) {
      const copy = new Float32Array(ch);          // detach from the reused render buffer
      this.port.postMessage(copy, [copy.buffer]); // transfer ownership (no clone)
    }
    return true;   // keep the processor alive until the node is disconnected
  }
}
registerProcessor("pcm-capture", PCMCapture);
