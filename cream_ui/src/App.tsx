// @ts-expect-error - React is needed for JSX
import React from 'react';
import { useState } from 'react';
import reactLogo from './assets/react.svg';
import viteLogo from '/vite.svg';
import { Button } from './components/ui/button';

import './App.css';

function App() {
  const [count, setCount] = useState(0);

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <div className="max-w-md mx-auto">
            <div className="flex items-center space-x-5">
              <a href="https://vitejs.dev" target="_blank" rel="noreferrer">
                <img src={viteLogo} className="h-12 w-12" alt="Vite logo" />
              </a>
              <a href="https://react.dev" target="_blank" rel="noreferrer">
                <img src={reactLogo} className="h-12 w-12 animate-spin" alt="React logo" />
              </a>
            </div>
            <div className="divide-y divide-gray-200">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <h1 className="text-3xl font-bold text-gray-900 mb-8">Vite + React</h1>
                <div className="space-y-4">
                  <button
                    onClick={() => setCount((count) => count + 1)}
                    className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
                  >
                    count is {count}
                  </button>
                  <p className="text-gray-600">
                    Edit <code className="bg-gray-100 px-2 py-1 rounded">src/App.tsx</code> and save
                    to test HMR
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="mt-8 text-center">
        <Button className="bg-purple-500 hover:bg-purple-600">Click me</Button>
      </div>
    </div>
  );
}

export default App;
