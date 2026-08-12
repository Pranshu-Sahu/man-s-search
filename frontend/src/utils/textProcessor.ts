export interface VocabItem {
  page_number: number;
  base_form: string;
  text_form: string;
  category: 'vocabulary' | 'phrasal_verb' | 'idiom' | 'domain_concept';
  cefr_level: 'C1' | 'C2' | 'Specialized';
  general_definition: string;
  contextual_definition: string;
  sample_sentence: string;
}

export interface BookPage {
  page_number: number;
  text: string;
}

/**
 * Safely processes raw page text into HTML paragraphs,
 * highlighting ONLY words/phrases that have definitions in vocabList.
 */
export function formatPageContent(rawText: string, vocabList: VocabItem[]): string {
  if (!rawText) return '';

  // Clean raw lines into clean paragraphs
  const rawParagraphs = rawText
    .split(/\n\s*\n/)
    .map(p => p.replace(/\s+/g, ' ').trim())
    .filter(p => p.length > 0);

  if (vocabList.length === 0) {
    return rawParagraphs.map((p, idx) => {
      const cls = idx === 0 ? 'first-letter-cap' : '';
      return `<p class="${cls}">${escapeHtml(p)}</p>`;
    }).join('');
  }

  // Sort vocab terms by length descending to avoid partial matches on multi-word phrases
  // We collect both text_form and base_form to match variants verbatim
  const sortedVocab: { term: string; vocabIndex: number }[] = [];
  const seenTerms = new Set<string>();

  vocabList.forEach((v, idx) => {
    [v.text_form, v.base_form].forEach(term => {
      if (term && term.trim().length > 1 && !seenTerms.has(term.toLowerCase())) {
        seenTerms.add(term.toLowerCase());
        sortedVocab.push({ term: term.trim(), vocabIndex: idx });
      }
    });
  });

  sortedVocab.sort((a, b) => b.term.length - a.term.length);

  return rawParagraphs.map((p, idx) => {
    let paragraphHtml = escapeHtml(p);

    // Apply highlights strictly for terms present in vocabList
    sortedVocab.forEach(({ term, vocabIndex }) => {
      const escapedTerm = escapeRegExp(term);
      // Match whole word/phrase boundaries
      const regex = new RegExp(`\\b(${escapedTerm})\\b`, 'gi');
      
      const vItem = vocabList[vocabIndex];
      const tooltipDef = escapeHtml(vItem.general_definition || vItem.contextual_definition);
      
      paragraphHtml = paragraphHtml.replace(regex, (match) => {
        return `<mark class="vocab-highlight" data-vocab-index="${vocabIndex}" title="${tooltipDef}">${match}</mark>`;
      });
    });

    const cls = idx === 0 ? 'first-letter-cap' : '';
    return `<p class="${cls}">${paragraphHtml}</p>`;
  }).join('');
}

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function escapeRegExp(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}
