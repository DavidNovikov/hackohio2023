const func = async () => {
  const response = await window.versions.ping()
  console.log(response) // prints out 'pong'
}

func()

Split(['#item-gallery', '#menu'], {
  minSize: 300,
  sizes: [75, 25],
})


let socket = null
window.versions.onPythonChildPort((event, port) => {
  console.log(`Python child process listening on port ${port}`)
  socket = new WebSocket(`ws://localhost:${port}`)
  socket.addEventListener('open', () => {
    console.log('WebSocket connection opened')
    buttonBegin.disabled = false
    buttonBegin.classList.remove('disabled')
    keepAlive()
  })
  socket.addEventListener('message', messageRecieved)

  socket.addEventListener('close', () => {
    console.log('WebSocket connection closed')
    socket = null
  })
  socket.addEventListener('error', (error) => {
    console.error('WebSocket connection error:', error)
  })
})

function keepAlive() {
  if (socket) {
      send('keepAlive')
      setTimeout(keepAlive, 10000); 
  }
}

function send(command, data={}) {
  if (socket) {
    const json = {
      command: command,
      data: data,
    }
    socket.send(JSON.stringify(json))
  } else {
    console.warn('WebSocket connection not opened')
  }
}

function messageRecieved(event) {
  console.log(event)
  if (typeof event.data !== 'string') {
    // video feed stream
    const blob = event.data
    const url = URL.createObjectURL(blob)
    feed.src = url
  } else {
    handleMessage(event.data)
  }
}

function handleMessage(message) {
  console.log('WebSocket messages received:', message)
  const json = JSON.parse(message)
  const command = json.command
  const data = json.data

  switch (command) {
    case 'itemInserted':
      itemInserted(data)
      break
    case 'itemRemoved':
      itemRemoved(data)
      break
    default:
      console.warn(`Unknown command '${command}'`)
  }
}

const buttonBegin = document.getElementById('button-begin')
const buttonStop = document.getElementById('button-stop')

const procedureStarted = document.getElementById('procedure-started')
const procedureElapsed = document.getElementById('procedure-elapsed')

let procedureStartTime = null
let procedureTimer = null

buttonBegin.addEventListener('click', () => {
  log('began procedure')

  buttonBegin.disabled = true
  buttonStop.disabled = false
  buttonBegin.classList.add('disabled')
  buttonStop.classList.remove('disabled')

  send('beginProcedure')

  procedureStartTime = new Date()

  procedureStarted.innerText = 'started at ' + procedureStartTime.toLocaleTimeString()
  beginProcedureTimer()
})

function beginProcedureTimer() {
  procedureTimer = setInterval(() => {
    const now = new Date()
    const elapsed = now - procedureStartTime
    const seconds = Math.floor(elapsed / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)

    const secondsPure = seconds % 60
    const minutesPure = minutes % 60
    const hoursPure = hours % 60

    const secondsString = secondsPure.toString().padStart(2, '0')
    const minutesString = minutesPure.toString().padStart(2, '0')
    const hoursString = hoursPure.toString().padStart(2, '0')

    procedureElapsed.innerText = `${hoursString}:${minutesString}:${secondsString}`
    if (!hoursPure && !minutesPure) {
      procedureElapsed.innerText = `${secondsString}`
    }
    else if (!hoursPure) {
      procedureElapsed.innerText = `${minutesString}:${secondsString}`
    }
  }, 1000)
}

buttonStop.addEventListener('click', () => {
  log('stopped procedure')

  buttonBegin.disabled = false
  buttonStop.disabled = true
  buttonBegin.classList.remove('disabled')
  buttonStop.classList.add('disabled')

  send('stopProcedure')

  clearInterval(procedureTimer)
  procedureTimer = null
  procedureStartTime = null
  procedureStarted.innerText = 'not started'

})


// items
const itemsTotal = document.getElementById('items-total')
const itemGallery = document.getElementById('gallery')
const items = []
function itemInserted(item) {
  log(`inserted item '${item.title}'`)

  item.id = items.length
  const itemElement = document.createElement('div')
  itemElement.classList.add('item')
  itemElement.setAttribute('data-id', item.id)

  const itemImage = document.createElement('img')
  itemImage.src = item.imageSrc
  itemElement.appendChild(itemImage)

  const itemContent = document.createElement('div')
  itemContent.classList.add('item-content')
  itemElement.appendChild(itemContent)

  const itemTitle = document.createElement('span')
  itemTitle.classList.add('title')
  itemTitle.innerText = item.title
  itemContent.appendChild(itemTitle)

  const itemAdded = document.createElement('p')
  itemAdded.innerHTML =  `Inserted at ${new Date().toLocaleTimeString()}`
  itemContent.appendChild(itemAdded)

  itemGallery.appendChild(itemElement)

  // full screen on click
  itemElement.addEventListener('click', () => {
    if (itemElement.classList.contains('selected')) {
      itemElement.classList.remove('selected')
    } else {
      document.querySelector('.item.selected')?.classList.remove('selected')
      itemElement.classList.add('selected')
    }
  })

  item.html = itemElement
  items.push(item)

  itemsTotal.innerText = items.length
}

function itemRemoved(item) {
  log(`removed item '${item.title}'`)
  const index = items.findIndex(i => i.title === item.title)
  if (index > -1) {
    items[index].html.remove()
    items.splice(index, 1)

    itemsTotal.innerText = items.length
  }
  console.warn(`Item '${item.title}' not found`)
}


// log
const logElement = document.getElementById('log-messages')
const logTitle = document.getElementById('log-title')
function log(message) {
  const messageElement = document.createElement('p')
  messageElement.innerText = new Date().toLocaleTimeString() + ' ' + message
  logElement.insertBefore(messageElement, logElement.firstChild)
}

logTitle.addEventListener('click', () => {
  logElement.classList.toggle('collapsed')
})



// feed
const feed = document.getElementById('feed')
