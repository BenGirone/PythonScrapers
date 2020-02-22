const HEADERS = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}

class Scraper {
    constructor(params) {
        this.params = params;
        this.frames = [];
        this.chunks = [];
    }

    get(indexer) {
        if (typeof indexer === 'object' && indexer.length === 3) {
            const start = indexer[0] || 0;
            const stop = indexer[1] || this.maxLength;
            const step = indexer[2] || 1;

            const items = [];
            for (let i = start; i < stop; i += step) {
                const item = this.get(i);
                if (item) {
                    items.push(this.get(i));
                } else {
                    break;
                }
            }

            return items;
        } else if (typeof indexer === 'number') {
            if (indexer < this.frames.length) {
                return this.frames[i];
            } else {
                const scrapeResult = this.scrape();

                if (scrapeResult) {
                    return this.get(i);
                } else {
                    return false;
                }
            }
        } else {
            throw 'Bad scraper indexer';
        }
    }

    scrape() {
        // Collects new frames
    }

    get length() {
        return this.frames.length;
    }

    get maxLength() {
        return Infinity;
    }
}

class Chunk {
    constructor(recipe, size = 0) {
        this.recipe = recipe;
        this.size = size;
    }
}

class Frame {
    constructor(params) {
        this.__rawParams = params;
    }
    
    get video() {
        return this.__rawParams.video;
    }
    
    get image() {
        return this.__rawParams.image;
    }
    
    get text() {
        return this.__rawParams.text;
    }
    
    get additionalText() {
        return this.__rawParams.additionalText;
    }
    
    get positiveMetric() {
        return this.__rawParams.positiveMetric;
    }
    
    get negativeMetric() {
        return this.__rawParams.negativeMetric;
    }
    
    get interactionMetric() {
        return this.__rawParams.interactionMetric;
    }
    
    get reference() {
        return this.__rawParams.reference;
    }

    toJson() {
        return JSON.stringify(this.__rawParams);
    }
}