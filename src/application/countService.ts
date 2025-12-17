const Count = require('../domain/count');

class CountService {
  constructor(repository) {
    this.count = new Count(repository);
  }

  async execute(tableName) {
    return await this.count.getCount(tableName);
  }
}

module.exports = CountService;
