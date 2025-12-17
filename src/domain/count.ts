class Count {
  constructor(repository) {
    this.repository = repository;
  }

  async getCount(tableName) {
    return this.repository.getCount(tableName);
  }
}

module.exports = Count;
