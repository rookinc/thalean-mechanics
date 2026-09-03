# Thalean Mechanics

Specification version: 0.2.0

Thalion ontology version: 0.1.0

Axiom version: 0.1.0

## Scope

The mechanics layer defines lawful structure involving a thalion
without enlarging the primitive ontology of the thalion.

Axiom 10 establishes the boundary:

    The ontology of the thalion is minimal.

    Further ablation invalidates the thalion.

    Further definition belongs to mechanics rather than ontology.

Accordingly, mechanics laws may extend Thalean Mechanics while the
minimal ontology remains unchanged.

## Current Mechanics Law

### Representation Completeness

See:

    mechanics/representation_completeness.md

A canonical thalion admits a lawful family of deterministic
registration interpreters whose joint action is faithful to Canonical
Registration.

For a family

    I_j : R_T -> X_j,

define the diagonal interpreter

    Delta_I(r) = (I_j(r))_j.

The family is jointly faithful when

    Delta_I

is injective.

Define the compatibility locus

    C_I = image(Delta_I).

For a jointly faithful interpreter family,

    Delta_I : R_T -> C_I

is bijective.

No individual interpreter is required to be injective.

## Ontology Boundary

Representation Completeness does not redefine the thalion.

It does not modify Axioms 1 through 10.

It does not identify Canonical Registration with:

- G60
- G30
- Actor120
- a graph state
- a bit
- a computational record
- registered history
- Thalean time

The thalion remains the primitive computational object.

Canonical Registration remains the objective source of
representations.

## Informative Action Boundary

Informative Action remains a lawful action capable of changing
Canonical Registration.

Representation Completeness does not by itself prove that Actor
Enactment changes Canonical Registration.

The ontology-to-mechanics source bridge remains open.

## Finite Motivating Model

Project 41 Audits 109D and 109E provide an independently derived finite
model of the Representation Completeness architecture.

Actor120 has three native sixty-state quotient shadows.

Each individual shadow is two-to-one.

Any two distinct shadows jointly recover the complete Actor state.

All three shadows share the native G30 base.

The raw three-shadow G30 fiber product contains 240 tuples.

The lawful Actor compatibility locus contains 120 tuples.

Locally the compatibility law is

    e xor h xor t = 0.

This finite theorem motivates the mechanics law.

It does not establish

    Actor120 = R_T.

The Actor quotient maps are not thereby promoted to registration
interpreters.

## Version Boundary

Thalean Mechanics specification: 0.2.0

Thalion ontology: 0.1.0

Axioms: 0.1.0

The mechanics specification may develop while the minimal thalion
ontology remains unchanged.
