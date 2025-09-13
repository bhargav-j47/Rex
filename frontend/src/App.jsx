import axios from 'axios'
import { useEffect, useState } from 'react'
import Split from 'react-split';
import Topbar from './components/Topbar'
import Editor from '@monaco-editor/react';
import Panel from './components/Panel';

const defaultCode = {
  python: "",
  cpp: ""
} // define default code for python and cpp here


function App() {

  // states
  const [lang, setLang] = useState("cpp")
  const [src, setSrc] = useState(defaultCode[lang])
  const [input, setInput] = useState("")
  const [expOut, setExpOut] = useState("")
  const [timeLimit, setTimeLimit] = useState(3);
  const [memLimit, setMemLimit] = useState(256);

  const [output, setOutput] = useState('');
  const [time, setTime] = useState(0);
  const [mem, setMem] = useState(0);

  const [isTimer, setIsTimer] = useState(false);
  const [timer, setTimer] = useState(0);

  const [isLoading, setIsLoading] = useState(false);

  //effects below

  useEffect(() => {
    let tref = [];
    if (isTimer) {
      tref = setInterval(setTimer(prev => prev + 1), 1000);
    }
    else {
      clearInterval(tref);
    }

    return () => clearInterval(tref);

  }, [isTimer])

  //functions below

  const handleLangChange = (lang) => {
    setLang(lang);
    setSrc(defaultCode[lang]);
  }

  const handleSrcChange = (code) => {
    setSrc(code);
  }

  const handleInputChange = (input) => { setInput(input) }
  const handleExpOutChange = (output) => { setExpOut(output) }
  const handleTimeLimitChange = (limit) => { setTimeLimit(limit) }
  const handleMemLimitChange = (limit) => { setMemLimit(limit) }

  const handleTimerChange = () => {
    if (!isTimer) setTimer(0);
    setIsTimer(prev => !prev);
  }


  const handleSubmit = async () => {
    const postData = {
      language: lang,
      input: input,
      exp_result: expOut,
      src: src,
      timeLimit: timeLimit,
      memLimit: (memLimit * 1000)
    }

    try {
      setIsLoading(true);
      const id = await axios.post('/api/submit', postData)
      check(id);

    } catch (error) {
      setError("unexpected error");
    } finally {
      setIsLoading(false);
    }

  }

  const check = async (id) => {
    try {
      let intref = setInterval(async () => {
        data = await axios.get(`/api/check?${id}`);
        data=JSON.parse(data);
        setOutput(data.output);

        if (output != "running" || output != "queued") {
          setTime(data.time);
          setMem(data.memory);
          return;
        }
      }, 2000)

      clearInterval(intref);
    }
    catch (error) {
      setError(error.message);
      return;
    }
  }



  return (
    <>
       <div className="flex flex-col h-screen w-screen bg-slate-900">
        <Topbar
          onLangChange={handleLangChange}
          selectedLang={lang}
          onTimerChange={handleTimerChange}
          isTimer={isTimer}
          timer={timer}
        />
        <Split className='className="flex flex-grow"' sizes={[50, 50]} minSize={300} direction='horizontal' >
          <div className="overflow-hidden bg-slate-900">
            <Editor
              height="100%"
              language={lang}
              theme="vs-dark"
              value={src}
              onChange={handleSrcChange}
              options={{ minimap: { enabled: false }, fontSize: 16, scrollBeyondLastLine: false }}
            />
          </div>
          <div className="overflow-hidden">
            <Panel/>
          </div>
        </Split>

      </div>
    </>
  )
}

export default App
