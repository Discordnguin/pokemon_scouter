// Get Pokémon artwork URL from Showdown's sprite CDN
// This uses full artwork images which are more reliable than sheet coordinates
function getIconStyle(pokemonName) {
    // Normalize the name to match Showdown's sprite naming
    // Examples: "Scizor-Mega" -> "scizor-mega", "Tapu Fini" -> "tapu-fini", etc.
    const normalized = pokemonName.toLowerCase()
        .replace(/[\s\-\.]/g, '') // Remove spaces, hyphens, dots
        .replace(/([a-z])([A-Z])/g, '$1-$2') // Handle camelCase
        .toLowerCase();
    
    // Create the artwork sprite URL
    // Showdown stores artwork at: https://play.pokemonshowdown.com/sprites/pokemon/[id].png
    // For Mega forms, they use: https://play.pokemonshowdown.com/sprites/pokemon/[id]-mega.png
    
    let spriteId = pokemonName.toLowerCase()
        .replace(/\s+/g, '-')  // Replace spaces with hyphens
        .replace(/[^\w\-]/g, '') // Remove special chars
        .replace(/--+/g, '-');  // Collapse multiple hyphens
    
    // Handle special cases
    if (spriteId.includes('mega')) {
        if (spriteId.includes('megax')) spriteId = spriteId.replace('megax', 'mega-x');
        else if (spriteId.includes('megay')) spriteId = spriteId.replace('megay', 'mega-y');
        else spriteId = spriteId.replace('mega', '-mega').replace('--', '-');
    }
    
    if (spriteId.includes('therian')) spriteId = spriteId.replace('therian', '-therian').replace('--', '-');
    if (spriteId.includes('ash')) spriteId = spriteId.replace('ash', '-ash').replace('--', '-');
    if (spriteId.includes('east')) spriteId = spriteId.replace('east', '-east').replace('--', '-');
    if (spriteId.includes('west')) spriteId = spriteId.replace('west', '-west').replace('--', '-');
    
    // Build the image URL
    const imageUrl = `https://play.pokemonshowdown.com/sprites/pokemon/${spriteId}.png`;
    
    // Return HTML/CSS to display as a small thumbnail
    // We'll use a different approach - return null and let script.js handle it
    return imageUrl;
}

