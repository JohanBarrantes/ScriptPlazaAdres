interface Repository {
  getCount(tableName: string): Promise<number>; 
}

class Count {
  private repository: Repository;

  constructor(repository: Repository) {
    this.repository = repository;
  }

  async getCount(tableName: string): Promise<number> {
    return this.repository.getCount(tableName);
  }
}

export default Count;
