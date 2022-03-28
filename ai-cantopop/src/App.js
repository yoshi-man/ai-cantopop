import React, { useState, useRef } from 'react';
import { ReactComponent as Spinner } from './Spinner.svg'
import axios
 from 'axios';
function App() {

  const seedInputRef = useRef()
  const lyricsLengthRef = useRef()

  const [isLoading, setIsLoading ] = useState(false)
  const [lyrics, setLyrics ] = useState("")
  const [errorMsg, setErrorMsg ] = useState(null)
  
  const areValidInputs = (seed, length)=> {
    if(String(seed).length === 0) {setErrorMsg('Invalid Seed Input.'); return false}
    if(String(seed).length > 12){setErrorMsg('Invalid Seed Input.'); return false}
    
    try{
        const length_input = parseInt(String(length))
        if(!length_input){setErrorMsg('Invalid Length Input. Input cannot be null.'); return false}
        if(length_input < 12){setErrorMsg('Invalid Length Input. Length has to be between 12 to 720'); return false}
        if(length_input > 720){setErrorMsg('Invalid Length Input. Length has to be between 12 to 720'); return false}
    } catch{
        setErrorMsg('Invalid Length Input.')
        return false
    }

    setErrorMsg(null)
    return true
}

  const getLyrics = (seed, length) => {
    axios.get('https://ai-cantopop.herokuapp.com/seed='+ seed + '&length=' + String(length))
    .then(response=>{
        setLyrics(response.data['BODY'])
        setIsLoading(false)
    }).catch( e =>{
        setLyrics(null)
        setIsLoading(false)
    }).finally(()=>{
      setIsLoading(false)
    })
}


  const handleGenerateLyricsButtonClick = () =>{
    setIsLoading(true)
    setLyrics('')
    setErrorMsg(null)

    const seed = seedInputRef.current.value
    const length = lyricsLengthRef.current.value

    if(!areValidInputs(seed, length)){
        setIsLoading(false)
        return ''
    }

    getLyrics(seed, length)
  }


  return (
    <div>
      <div className="flex flex-col justify-center items-center ">
        <div className="w-full sm:w-9/12 h-24 flex items-center px-6 ">
          <h1 className="text-3xl font-semibold border-b-2 h-full w-full flex items-center
          sm:text-4xl">Cantopop Lyrics Generator</h1>
        </div>

        <div className="w-full px-6 py-6 sm:w-9/12 ">
          <h1 className="text-2xl font-semibold w-full h-full">Welcome</h1>
          <p className="text-lg w-full h-full mt-4">
            Hey there! I see that you&apos;re interested in making your own cantopop, get the lyrics part out the way by generating your own set of lyrics.
          </p>
        </div>

        
        <div className="w-full px-6 py-6 sm:w-9/12 ">
          <h1 className="text-2xl font-semibold w-full h-full">How does it work?</h1>
          <p className="text-lg w-full h-full mt-4">
            If you&apos;re interested in how things work in the backend, do visit this link to learn more from the <a target="_blank" className="text-blue-500 underline" href="https://github.com/yoshi-man/ai-cantopop"> Github source code</a>.
          </p>
        </div>

        
        <div className="w-full px-6 py-6 sm:w-9/12 ">
          <h1 className="text-2xl font-semibold w-full h-full">Generate My Lyrics</h1>
          <div className="w-full flex flex-col justify-center items-start">
          <p className="text-lg w-full h-full mt-4">
            To get started, scroll down to input your seed phrase, it can be anything but <span className="font-semibold text-blue-500">keep it within 12 characters</span>. The length will be the total number of characters for the lyrics, <span className="font-semibold text-blue-500">keep it within 720 characters</span>.
          </p>

          <label for="seed" className="font-semibold text-base mt-4 mb-2">Seed Phrase</label>
          <input name="seed" className={"px-4 py-2 border-2 w-full rounded-md" + (errorMsg?.includes('Seed') ? " border-red-500": (lyrics === "" ? "" : " border-green-500"))} ref={seedInputRef} placeholder="e.g. 你好世界" />
          <label for="length" className="font-semibold text-base mt-4 mb-2">Lyrics Length</label>
          <input name="length" className={"px-4 py-2 border-2 w-full rounded-md" + (errorMsg?.includes('Length') ? " border-red-500": (lyrics === "" ? "" : " border-green-500"))} ref={lyricsLengthRef} placeholder="e.g. 700" />

          <label for="results" className="font-semibold text-base mt-4 mb-2">Your Lyrics</label>
          <p name="results" className={"whitespace-pre-line text-base text-gray-600 w-full h-full min-h-[300px] px-4 py-2 border-2 border-solid rounded-md" + (errorMsg ? " border-red-500": (lyrics === "" ? "" : " border-green-500"))}>
            { 
              isLoading ? <div className="w-full h-full flex justify-center items-center"><Spinner /></div>  : 
              (
              errorMsg ? 
              <p className="text-red-500 font-semibold">{errorMsg}</p> 
              :
              lyrics
              )
            }
          </p>

          <button className="p-2 rounded-md bg-gray-500 text-white mt-4
          hover:bg-blue-500" onClick={()=>{handleGenerateLyricsButtonClick()}}>
            {isLoading ? "Loading..." :"Generate Lyrics" 
            }
          </button>
          </div>
        </div>



      </div>


    </div>
  );
}

export default App;
