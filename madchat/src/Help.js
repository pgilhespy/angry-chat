import React, { useState, useEffect } from "react";
import './Help.css';

const Help = () => {
    // State to store the waitlist number
    const [waitlistNumber, setWaitlistNumber] = useState(null);

    const getRandomNumber = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

    useEffect(() => {
        setWaitlistNumber(getRandomNumber(15, 40));

        const decrementWaitlist = () => {
            setWaitlistNumber(prevNumber => prevNumber - getRandomNumber(1,5));

            // Schedule next decrement at a random interval (1 to 5 seconds)
            const randomDelay = getRandomNumber(1000, 5000);
            setTimeout(decrementWaitlist, randomDelay);
        };

        // Start first decrement
        const initialDelay = getRandomNumber(1000, 5000);
        const timeoutId = setTimeout(decrementWaitlist, initialDelay);

        return () => clearTimeout(timeoutId);
    }, []);

    return (
        <div className="loading-container">
            <p className="loading-message">Please hold as we connect you with support</p>
            <div className="loading-spinner"></div>
            {waitlistNumber !== null && <p className="loading-message">Your spot in the waitlist: {waitlistNumber}</p>}
        </div>
      );
  };
  
  export default Help;