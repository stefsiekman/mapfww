export class PriorityQueue {

  /**
   * @param comparator Compare A & B, should return whether A can be in front of
   * B in the queue.
   */
  constructor(comparator) {
    this.comparator = comparator;
    this.items = [];
  }

  enqueue(element) {
    for (let i = 0; i < this.items.length; i++) {
      if (this.comparator(element, this.items[i])) {
        this.items.splice(i, 0, element);
        return;
      }
    }
    this.items.push(element);
  }

  dequeue() {
    console.assert(!this.empty, 'Dequeue from non-empty queue');
    return this.items.shift();
  }

  get empty() {
    return this.items.length === 0;
  }

}