import './App.css';
import { ChatWidgetComponent } from './components/ChatWidgetComponent';
import { ListPlaylistButton } from './components/ListPlaylistButton';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <ChatWidgetComponent />
        <ListPlaylistButton />
      </header>
    </div>
  );
}

export default App;
