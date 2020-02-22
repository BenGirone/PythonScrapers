class Reddit extends Scraper {
    constructor(params) {
        super(params);

        this.query = params.query;
        this.shouldGetTextAndComments = params.shouldGetTextAndComments;
        this.canScrape = true;
        this.chunks.push(new Chunk(''));
        this.scrape();
    }

    scrape() {
        if (!this.canScrape) {
            return false;
        }


        try {
            
            return true;
        } catch (error) {
            console.error(error);
            return false;
        }
    }
}