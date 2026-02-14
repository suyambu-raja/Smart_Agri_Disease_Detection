
import fs from 'fs';
import path from 'path';
import { createCanvas } from 'canvas';

// Helper to create a simple icon
function createIcon(size, text, filename) {
    const canvas = createCanvas(size, size);
    const ctx = canvas.getContext('2d');

    // Background
    ctx.fillStyle = '#10b981'; // Emerald/Green color
    ctx.fillRect(0, 0, size, size);

    // Text
    ctx.fillStyle = 'white';
    ctx.font = `bold ${size / 4}px Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('Agri', size / 2, size / 2);

    const buffer = canvas.toBuffer('image/png');
    fs.writeFileSync(path.join(process.cwd(), 'public', filename), buffer);
    console.log(`Created ${filename}`);
}

// Ensure public dir exists (it should)
if (!fs.existsSync('public')) {
    fs.mkdirSync('public');
}

// Create icons
try {
    createIcon(192, 'SA', 'pwa-192x192.png');
    createIcon(512, 'SA', 'pwa-512x512.png');
    // Also create an apple-touch-icon if missing
    createIcon(180, 'SA', 'apple-touch-icon.png');
} catch (e) {
    console.error("Error creating icons:", e);
}
