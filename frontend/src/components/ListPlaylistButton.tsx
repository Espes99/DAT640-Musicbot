import React, { useState } from 'react';
import './ListPlaylistButton.css';

interface Song {
    id: number;
    name: string;
    artist: string;
    length: string;
}

export const ListPlaylistButton: React.FC = () => {
    const [showPlaylist, setShowPlaylist] = useState(false);

    //Should get playlist from backend
    const playlist: Song[] = [
        { id: 1, name: 'Here Comes the Sun', artist: 'The Beatles', length: '3:05' },
        { id: 2, name: 'Bohemian Rhapsody', artist: 'Queen', length: '5:55' },
        { id: 3, name: 'Imagine', artist: 'John Lennon', length: '3:01' },
    ];

    const togglePlaylist = () => {
        setShowPlaylist(!showPlaylist);
    };

    return (
        <div className="container">
            <button className="toggle-button" onClick={togglePlaylist}>
                {showPlaylist ? 'Hide Playlist' : 'Show Playlist'}
            </button>
            {showPlaylist && (
                <div className="playlist">
                    {playlist.map((song) => (
                        <div key={song.id} className="song-card">
                            <h3>{song.name}</h3>
                            <p>{song.artist}</p>
                            <p>{song.length}</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};
