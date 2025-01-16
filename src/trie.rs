use std::collections::HashMap;
use fxhash::FxBuildHasher;

type FxHashMap<K, V> = HashMap<K, V, FxBuildHasher>;

#[derive(Default, Debug)]
struct TrieNode<K> {
    is_end_of_word: bool,
    children: FxHashMap<K, TrieNode<K>>,
}

impl<K> Default for TrieNode<K> 
where
    K: std::hash::Hash + Eq + Clone,
{
    fn default() -> Self {
        TrieNode {
            is_end_of_word: false,
            children: FxHashMap::default(),
        }
    }
}


#[derive(Default, Debug)]
pub struct Trie<K> {
    root: TrieNode<K>,
}

impl<K> Trie<K> 
where 
    K: std::hash::Hash + Eq + Clone,
{
    pub fn new() -> Self {
        Trie {
            root: TrieNode::<K>::default(),
        }
    }

    pub fn insert(&mut self, word: &[K]) {
        let mut current_node = &mut self.root;

        for &c in word {
            current_node = current_node.children.entry(c.clone()).or_default();
        }
        current_node.is_end_of_word = true;
    }

    pub fn contains(&self, word: &[K]) -> bool {
        let mut current_node = &self.root;

        for c in word {
            match current_node.children.get(&c) {
                Some(node) => current_node = node,
                None => return false,
            }
        }

        current_node.is_end_of_word
    }
}

fn main() {
    let mut trie = Trie::new();
    trie.insert("hello");
    trie.insert("hi");
    trie.insert("hey");
    trie.insert("world");

    println!("{trie:#?}");

    println!("hiiii? {}", trie.contains("hiiii"));
}