// const PORT = 8000
// const express = require('express')
// const cors = require('cors')
// require('dotenv').config()
// const app = express()
// app.use(express.json())
// app.use(cors())

// const API_KEY= process.env.API_KEY

// app.post('/completions', async(req, res) => {
//     const options = {
//         method:"POST",
//         header: {
//             "Authorization": `Bearer ${API_KEY}`,
//             "Content-Type": "application/json"
//         },
//         body: JSON.stringify({
//             model: "placeholder",
//             messages: [{ role: "user", content: req.body.message}],
//             max_tokens: 1000
//         })
//     }
//     try{
//         const response = await fetch('placeholder', options)
//         const data = await response.json()
//         res.send(data)
//     } catch(error) {
//         console.error(error)
//     }
// })

// app.listen(PORT,  () => console.log('Your server is running on PORT ' + PORT))

// /*app.post('/completions', async (req, res) => {
//     const userMessage = req.body.message; // Get user input from request
    
//     // Dummy AI response
//     const mockResponse = {
//         choices: [
//             {
//                 message: {
//                     role: "assistant",
//                     content: `I'm Angry Bot! You said: "${userMessage}", and I don't care.`
//                 }
//             }
//         ]
//     };

//     res.send(mockResponse); // Send mock response instead of making an API call
// });
// app.listen(PORT,  () => console.log('Your server is running on PORT ' + PORT))*/
