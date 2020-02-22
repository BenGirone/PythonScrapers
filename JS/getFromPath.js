function safeGet(data, datapath, def = null) {
    const pathParts = datapath.split('.')

    let dataPart = data;

    try {
        for (let part of pathParts) {
            if (part.startsWith('[')) {
                dataPart = dataPart[JSON.parse(part)[0]];
            } else {
                dataPart = dataPart[part];
            }
        }

        return dataPart;
    } catch (error) {
        return def;
    }
}