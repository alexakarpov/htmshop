describe('a first spec', () => {
  it('has our title', () => {
      cy.visit('localhost:8000')
      cy.title().should('eq', 'HTM Store')
  })
})
