#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk

class ListNode:
    def __init__(self, category, length):
        self.category = category
        self.length = length
        self.next = None

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_word = False
        self.word_list_head = None  # Head of linked list

    def add_to_word_list(self, category, length):
        new_node = ListNode(category, length)
        if not self.word_list_head:
            self.word_list_head = new_node
        else:
            current = self.word_list_head
            while current.next:
                current = current.next
            current.next = new_node

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def load_words(self, word_category_length_list):
        for word, category, length in word_category_length_list:
            self.add_word(word, category, length)

    def add_word(self, word, category, length):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True
        node.add_to_word_list(category, length)

    def auto_correct(self, word):
        node = self.root
        if word[0] not in node.children:
            return [word]
        for i, char in enumerate(word):
            if char not in node.children:
                return self.auto_fill(word[:i], node)
            node = node.children[char]
        return [word]

    def auto_fill(self, prefix, node=None):
        if node is None:
            node = self.root
            for char in prefix:
                if char not in node.children:
                    return []
                node = node.children[char]
        words = []
        if node.is_word:
            words.append((prefix, node.word_list_head.category, node.word_list_head.length))
        for char, child in node.children.items():
            words.extend(self.auto_fill(prefix + char, child))
        return words

    def spell_check(self, sentence):
        words = sentence.split()
        misspelled = []
        for word in words:
            if not self.check_word(word):
                misspelled.append(word)
        return misspelled

    def check_word(self, word):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                return False
            node = node.children[char]
        return node.is_word

    def words_under_category(self, category):
        node = self.root
        words = []
        self.get_words_under_category(node, category, "", words)
        return words

    def get_words_under_category(self, node, category, prefix, words):
        if node.is_word and node.word_list_head.category == category:
            words.append(prefix)
        for char, child in node.children.items():
            self.get_words_under_category(child, category, prefix + char, words)

class MyApplication:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Text Optimization")
        self.root.geometry("800x600") 
        self.root.configure(bg="sky blue")
        self.root.resizable(False, False) 

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("TButton",
                             padding=15, 
                             relief="flat",
                             foreground="white",
                             background="#4CAF50",
                             font=('Helvetica', 12, 'bold'))
        self.style.map("TButton",
                       foreground=[('active', 'white')],
                       background=[('active', '#45a049')],
                       relief=[('pressed', 'groove'), ('!pressed', 'flat')])
        
        self.style.configure("TLabel", padding=6, background="sky blue", foreground="#333333", font=('Helvetica', 14, 'bold'))

        self.trie = Trie()
        with open('temp.txt') as f:
            word_category_length_list = [line.split() for line in f.readlines()]
        self.trie.load_words(word_category_length_list)

        self.label = ttk.Label(self.root, text="Enter a sentence:")
        self.label.pack(pady=(20, 10))

        self.textbox = tk.Text(self.root, font=('Helvetica', 12), width=80, height=5)  
        self.textbox.pack(pady=10, padx=20)

        self.button_frame = tk.Frame(self.root, bg="sky blue")
        self.button_frame.pack(pady=10)

        self.correct_button = ttk.Button(self.button_frame, text="Auto Correct", command=self.auto_correct)
        self.correct_button.grid(row=0, column=0, padx=10, pady=10)

        self.suggest_button = ttk.Button(self.button_frame, text="Auto Suggest", command=self.auto_suggest)
        self.suggest_button.grid(row=0, column=1, padx=10, pady=10)

        self.check_button = ttk.Button(self.button_frame, text="Spell Check", command=self.spell_check)
        self.check_button.grid(row=1, column=0, padx=10, pady=10)

        self.category_button = ttk.Button(self.button_frame, text="Check by Category", command=self.check_category)
        self.category_button.grid(row=1, column=1, padx=10, pady=10)

        self.words_under_category_button = ttk.Button(self.button_frame, text="Check Words under Category", command=self.words_under_category)
        self.words_under_category_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.result_label = ttk.Label(self.root, text="", wraplength=750)  # Increased wraplength
        self.result_label.pack(pady=10, padx=20)

    def auto_correct(self):
        word = self.textbox.get("1.0", tk.END).strip()
        corrected_words = self.trie.auto_correct(word)
        cv = list(word)
        ll = {}
        for i in corrected_words:
            if len(i) == len(word):
                print(i)
            ll[i] = 0
        for i in ll:
            for j in cv:
                if j in i:
                    ll[i] += 1
        print("Mostly resembles the word:", max(ll, key=ll.get))
        self.result_label.config(text="Corrected word: " + max(ll, key=ll.get)[0])

    def auto_suggest(self):
        prefix = self.textbox.get("1.0", tk.END).strip()
        words = self.trie.auto_fill(prefix)
        suggestions = "\n".join([f"{word[0]} ({word[1]}, {word[2]})" for word in words])
        self.result_label.config(text="Suggested words:\n" + suggestions)

    def spell_check(self):
        sentence = self.textbox.get("1.0", tk.END).strip()
        misspelled_words = self.trie.spell_check(sentence)
        if not misspelled_words:
            self.result_label.config(text="No misspelled words found.")
        else:
            self.result_label.config(text="Misspelled words: " + ", ".join(misspelled_words))

    def check_category(self):
        word = self.textbox.get("1.0", tk.END).strip()
        words = self.trie.auto_fill(word)
        for w in words:
            if w[0] == word:
                self.result_label.config(text=f"The category of '{word}' is '{w[1]}'.")
                return
        self.result_label.config(text=f"'{word}' not found in the dictionary.")

    def words_under_category(self):
        category = self.textbox.get("1.0", tk.END).strip()
        words = self.trie.words_under_category(category)
        if not words:
            self.result_label.config(text=f"No words found under category '{category}'.")
        else:
            self.result_label.config(text=f"Words under category '{category}':\n" + ", ".join(words))

    def run(self):
        self.root.mainloop()

app = MyApplication()
app.run()

