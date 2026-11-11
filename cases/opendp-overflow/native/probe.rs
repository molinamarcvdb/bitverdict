use opendp::core::Domain;
use opendp::error::Fallible;
use opendp::trans::make_bounded_sum;

const UPPER: i32 = 1 << 30;

#[unsafe(no_mangle)]
#[inline(never)]
extern "C" fn probe_anchor() {}

fn print_layout(sum: &dyn Fn(&Vec<i32>) -> Fallible<i32>) {
    // The pinned compiler's trait object contains the data and vtable pointers.
    // The extractor checks that the call slot names the real OpenDP closure.
    let (_, vtable): (*const u8, *const usize) = unsafe { std::mem::transmute(sum) };
    assert_eq!(unsafe { *vtable.add(1) }, 0);
    let delta = unsafe { *vtable.add(5) } as isize - probe_anchor as *const () as isize;
    println!("fixture sum {delta} empty");

    let mut row = Vec::with_capacity(8);
    row.extend([1i32, 2, 3]);
    assert_eq!(std::mem::size_of::<Vec<i32>>(), 24);
    let raw = &row as *const Vec<i32> as *const usize;
    let words = unsafe { [raw.read(), raw.add(1).read(), raw.add(2).read()] };
    let slot = |v| words.iter().position(|&word| word == v).unwrap();
    println!("fixture vec {} {} {}", slot(row.capacity()), slot(row.as_ptr() as usize), slot(row.len()));
}

fn main() {
    let transform = make_bounded_sum::<i32>(0, UPPER).unwrap();
    print_layout(transform.function.function.as_ref());
    let rows = [
        vec![UPPER - 1],
        vec![UPPER, UPPER - 1],
        vec![UPPER, UPPER - 1, 1],
        vec![UPPER, UPPER - 1, 0],
    ];
    let values = rows.map(|row| {
        assert!(transform.input_domain.member(&row).unwrap());
        transform.function.eval(&row).unwrap()
    });
    let map = transform.stability_relation.forward_map.as_ref().unwrap();
    let zero_bound = *map(&0).unwrap();
    let bound = *map(&1).unwrap();
    assert_eq!(zero_bound, 0);
    assert_eq!(bound, UPPER);
    let expected = if cfg!(feature = "historical_bug") { i32::MIN } else { i32::MAX };
    assert_eq!(values, [UPPER - 1, i32::MAX, expected, i32::MAX]);
    println!("sums {values:?}");
    println!("zero-insertion bound {zero_bound}");
    println!("one-insertion bound {bound}");
}
