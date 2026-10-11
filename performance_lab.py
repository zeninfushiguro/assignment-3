import timeit
import tracemalloc


# 🔍 Problem 1: Find Most Frequent Element
# Given a list of integers, return the value that appears most frequently.
# If there's a tie, return any of the most frequent.
#
# Example:
# Input: [1, 3, 2, 3, 4, 1, 3]
# Output: 3

def most_frequent(numbers):
    if not numbers:
        return None
    counts = {}
    best_value = numbers[0]
    best_count = 0
    for n in numbers:
        counts[n] = counts.get(n, 0) + 1
        if counts[n] > best_count:
            best_count = counts[n]
            best_value = n
    return best_value


"""
Time and Space Analysis for problem 1:
- Best-case: O(n). Even if the first element dominates, we cannot know that
  without reading the whole list, so every case reads all n items once.
- Worst-case: O(n) with normal hashing. (Theoretical O(n^2) if every key
  collides in the dict, which does not happen with Python ints in practice.)
- Average-case: O(n). Each dict get/set is O(1) on average.
- Space complexity: O(k), where k = number of distinct values (O(n) worst case,
  when all values are unique; O(1) extra if the list is all one value).
- Why this approach? A dict counts each value in a single pass. The obvious
  alternative, calling list.count() for each element, is O(n^2).
  I also track the current best during the counting loop, so there is no
  second pass over the dict to find the max.
- Could it be optimized? Not asymptotically: O(n) time is a lower bound since
  every element must be read. collections.Counter(...).most_common(1) is the
  same Big O but faster in practice (counting is done in C). Trade-off: if you
  only need a strict majority element (> n/2), Boyer-Moore voting gets O(1)
  space, but it does not answer "most frequent" when no majority exists.
"""


# 🔍 Problem 2: Remove Duplicates While Preserving Order
# Write a function that returns a list with duplicates removed but preserves order.
#
# Example:
# Input: [4, 5, 4, 6, 5, 7]
# Output: [4, 5, 6, 7]

def remove_duplicates(nums):
    seen = set()
    result = []
    for n in nums:
        if n not in seen:
            seen.add(n)
            result.append(n)
    return result


"""
Time and Space Analysis for problem 2:
- Best-case: O(n). All items must still be checked, even if all are duplicates.
- Worst-case: O(n) with normal hashing (O(n^2) only under pathological hash
  collisions).
- Average-case: O(n). Set membership test and add are O(1) on average.
- Space complexity: O(n) worst case (all unique: the set and the result each
  hold n items). O(k) for k distinct values.
- Why this approach? The set gives O(1) "have I seen this?" checks. Checking
  `if n not in result` on the list instead would be O(n) per check and O(n^2)
  total. The separate result list is what preserves the original order, since
  sets do not.
- Could it be optimized? Asymptotically no. A shorter version is
  list(dict.fromkeys(nums)), since dicts keep insertion order; same Big O, less
  code. Trade-off: if memory is tight and the list is already sorted, you can
  dedupe in O(1) extra space by comparing neighbors, but that only works on
  sorted input (sorting first would cost O(n log n) and lose the original order).
"""


# 🔍 Problem 3: Return All Pairs That Sum to Target
# Write a function that returns all unique pairs of numbers in the list that sum to a target.
# Order of output does not matter. Assume input list has no duplicates.
#
# Example:
# Input: ([1, 2, 3, 4], target=5)
# Output: [(1, 4), (2, 3)]

# ORIGINAL VERSION (brute force), kept for the comparison in the "Optimize One" step.
def find_pairs_original(nums, target):
    pairs = []
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                pairs.append((min(nums[i], nums[j]), max(nums[i], nums[j])))
    return pairs


# REFACTORED VERSION (this is the "Optimize One" solution).
# Optimization: instead of comparing every pair (O(n^2) time, O(1) extra space),
# remember the numbers already seen in a set and look up each number's
# complement (target - x) in O(1). That is O(n) time at the cost of O(n) space.
def find_pairs(nums, target):
    seen = set()
    pairs = []
    for x in nums:
        complement = target - x
        if complement in seen:
            pairs.append((min(x, complement), max(x, complement)))
        seen.add(x)
    return pairs


"""
Time and Space Analysis for problem 3 (analysis of the ORIGINAL brute force
version first, then the refactored version):

ORIGINAL (find_pairs_original):
- Best-case: O(n^2). The nested loops always run all n(n-1)/2 comparisons,
  even if a pair is found right away, because we must find ALL pairs.
- Worst-case: O(n^2).
- Average-case: O(n^2).
- Space complexity: O(1) extra, not counting the output list.
- Why this approach? It is the simplest correct solution: check every pair.

REFACTORED (find_pairs):
- Best-case: O(n). One pass over the list.
- Worst-case: O(n) (O(n^2) only under pathological hash collisions).
- Average-case: O(n). Each set lookup/insert is O(1) on average.
- Space complexity: O(n) for the set, plus the output list.
- Could it be optimized further? Not in time: O(n) is a lower bound because
  every element must be read. A two-pointer approach on a sorted list uses
  O(1) extra space but costs O(n log n) to sort first.

Trade-offs: the refactor trades memory for speed (O(1) -> O(n) space for
O(n^2) -> O(n) time). For tiny lists the brute force is fine and the set
overhead is not worth it; for large lists the speedup is dramatic.
The function relies on the "no duplicates" assumption. With duplicates, the
set version would need a Counter to handle cases like [2, 2] with target 4.

OPTIMIZATION COMPARISON (measured with benchmark_find_pairs() at the bottom of
this file; exact numbers vary by machine):
- Time:   n=2,000: original ~84.5 ms vs refactored ~0.36 ms (about 230x faster).
          The gap grows with n, since O(n^2) vs O(n).
- Space:  peak memory (tracemalloc) at n=2,000: original ~8.9 KB vs
          refactored ~169.2 KB. The set is the extra cost, as predicted:
          roughly 19x more memory for roughly 230x less time.
"""


# 🔍 Problem 4: Simulate List Resizing (Amortized Cost)
# Create a function that adds n elements to a list that has a fixed initial capacity.
# When the list reaches capacity, simulate doubling its size by creating a new list
# and copying all values over (simulate this with print statements).
#
# Example:
# add_n_items(6) → should print when resizing happens.

def add_n_items(n, initial_capacity=2):
    capacity = initial_capacity
    storage = [None] * capacity
    size = 0
    total_copies = 0  # number of element copies done by resizes

    for item in range(n):
        if size == capacity:
            new_capacity = capacity * 2
            new_storage = [None] * new_capacity
            for i in range(size):          # copy every existing value: O(size)
                new_storage[i] = storage[i]
            total_copies += size
            print(f"Resize: capacity {capacity} -> {new_capacity}, copied {size} items")
            storage = new_storage
            capacity = new_capacity
        storage[size] = item
        size += 1

    print(f"Added {n} items. Final capacity: {capacity}. Total copies: {total_copies}")
    return total_copies


"""
Time and Space Analysis for problem 4:
- When do resizes happen? Whenever the list is full and a new item arrives.
  With initial capacity 2: when adding item 3 (2 -> 4), item 5 (4 -> 8),
  item 9 (8 -> 16), and so on. Resizes happen at sizes c, 2c, 4c, 8c, ...,
  so only about log2(n) resizes happen for n appends.
- What is the worst-case for a single append? O(n): the append that triggers a
  resize copies all n existing items.
- What is the amortized time per append overall? O(1). Total copy work for n
  appends is at most c + 2c + 4c + ... < 2n, plus n writes for the appends
  themselves, so about 3n total operations / n appends = O(1) per append.
- Space complexity: O(n). During a resize both the old and new arrays exist
  briefly (n + 2n = 3n slots), and afterwards capacity is at most 2x the
  size, so at most about half the allocated slots are unused.
- Why does doubling reduce the cost overall? Because each resize is expensive
  but rare, and each one doubles the room for future cheap appends. If we grew
  by a fixed amount (e.g. +10), resizes would happen every 10 appends and the
  copy work would sum to O(n^2), giving O(n) amortized per append. Trade-off:
  doubling wastes up to 50% of memory in exchange for the O(1) amortized speed.
"""


# 🔍 Problem 5: Compute Running Totals
# Write a function that takes a list of numbers and returns a new list
# where each element is the sum of all elements up to that index.
#
# Example:
# Input: [1, 2, 3, 4]
# Output: [1, 3, 6, 10]
# Because: [1, 1+2, 1+2+3, 1+2+3+4]

def running_total(nums):
    totals = []
    total = 0
    for n in nums:
        total += n
        totals.append(total)
    return totals


"""
Time and Space Analysis for problem 5:
- Best-case: O(n). The empty list is O(1), but any non-empty input still
  requires reading every element once.
- Worst-case: O(n).
- Average-case: O(n).
- Space complexity: O(n) for the new output list (O(1) extra beyond the output).
- Why this approach? Each total is the previous total plus the current number,
  so we keep one running sum and never re-add earlier elements. The naive way,
  calling sum(nums[:i+1]) for each index, is O(n^2) because it re-adds the
  same prefix over and over.
- Could it be optimized? Not asymptotically: the output itself has n items.
  itertools.accumulate(nums) does the same thing in C and is faster in
  practice. If modifying the input is allowed, computing in place uses O(1)
  extra space, at the cost of destroying the original data.
"""


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------
def run_tests():
    # Problem 1
    assert most_frequent([1, 3, 2, 3, 4, 1, 3]) == 3
    assert most_frequent([7]) == 7
    assert most_frequent([]) is None
    assert most_frequent([5, 5, 5, 5]) == 5
    assert most_frequent([1, 2, 2, 1]) in (1, 2)          # tie: either is valid
    assert most_frequent([-1, -1, 0]) == -1

    # Problem 2
    assert remove_duplicates([4, 5, 4, 6, 5, 7]) == [4, 5, 6, 7]
    assert remove_duplicates([]) == []
    assert remove_duplicates([1]) == [1]
    assert remove_duplicates([2, 2, 2, 2]) == [2]
    assert remove_duplicates([1, 2, 3]) == [1, 2, 3]

    # Problem 3 (compare as sets since order does not matter)
    for fn in (find_pairs_original, find_pairs):
        assert set(fn([1, 2, 3, 4], 5)) == {(1, 4), (2, 3)}
        assert fn([], 5) == []
        assert fn([3], 6) == []                           # no self-pairing
        assert fn([1, 2, 3], 100) == []
        assert set(fn([-1, 1, 0, 5, -5], 0)) == {(-1, 1), (-5, 5)}
        assert len(fn([1, 2, 3, 4], 5)) == 2

    # Problem 4
    assert add_n_items(0) == 0
    assert add_n_items(2) == 0                            # fits, no resize
    assert add_n_items(3) == 2                            # one resize copying 2
    assert add_n_items(6) == 2 + 4                        # resizes at 3rd and 5th item
    assert add_n_items(9) == 2 + 4 + 8

    # Problem 5
    assert running_total([1, 2, 3, 4]) == [1, 3, 6, 10]
    assert running_total([]) == []
    assert running_total([5]) == [5]
    assert running_total([-1, 1, -1]) == [-1, 0, -1]
    assert running_total([0, 0, 0]) == [0, 0, 0]

    print("All tests passed.")


def benchmark_find_pairs(n=2000):
    nums = list(range(n))
    target = n  # many valid pairs, no duplicates

    t_orig = timeit.timeit(lambda: find_pairs_original(nums, target), number=3) / 3
    t_fast = timeit.timeit(lambda: find_pairs(nums, target), number=3) / 3

    def peak(fn):
        tracemalloc.start()
        fn(nums, target)
        _, p = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return p

    print(f"find_pairs n={n}: original {t_orig * 1000:.2f} ms, "
          f"refactored {t_fast * 1000:.2f} ms")
    print(f"peak memory: original {peak(find_pairs_original) / 1024:.1f} KB, "
          f"refactored {peak(find_pairs) / 1024:.1f} KB")


if __name__ == "__main__":
    run_tests()
    benchmark_find_pairs()