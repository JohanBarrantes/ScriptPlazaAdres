import Count from '../domain/count';

class CountService {
  private count: Count;

  constructor(repository: any) {
    this.count = new Count(repository);
  }

  async execute(tableName: string): Promise<any> {
    return await this.count.getCount(tableName);
  }
}

export default CountService;
